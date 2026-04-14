/* Connect-4 front-end: board interaction + tree visualisation */

(function () {
    "use strict";

    const ROWS = 6;
    const COLS = 7;

    let board = [];
    let gameOver = false;
    let thinking = false;

    /* ---- DOM refs ---- */
    const boardEl = document.getElementById("board");
    const statusEl = document.getElementById("status");
    const depthInput = document.getElementById("depth");
    const depthValue = document.getElementById("depth-value");
    const algoSelect = document.getElementById("algorithm");
    const newGameBtn = document.getElementById("new-game");
    const treeSvg = document.getElementById("tree-svg");
    const treeStats = document.getElementById("tree-stats");

    /* ---- Initialisation ---- */
    function initBoard() {
        board = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
        gameOver = false;
        thinking = false;
        statusEl.textContent = "Your turn – click a column!";
        treeSvg.innerHTML = "";
        treeStats.textContent = "";
        renderBoard();
    }

    function renderBoard() {
        boardEl.innerHTML = "";
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                const cell = document.createElement("div");
                cell.classList.add("cell");
                if (board[r][c] === 1) cell.classList.add("player");
                else if (board[r][c] === 2) cell.classList.add("ai");
                cell.dataset.col = c;
                cell.addEventListener("click", () => handleClick(c));
                boardEl.appendChild(cell);
            }
        }
    }

    /* ---- Player move ---- */
    async function handleClick(col) {
        if (gameOver || thinking) return;
        if (!isValidCol(col)) return;

        thinking = true;
        statusEl.textContent = "Checking your move…";

        try {
            const res = await fetch("/api/check", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ board, col }),
            });
            const data = await res.json();
            if (data.error) { statusEl.textContent = data.error; thinking = false; return; }

            board = data.board;
            renderBoard();

            if (data.winner === "player") {
                statusEl.textContent = "🎉 You win!";
                gameOver = true;
                highlightWin(1);
                thinking = false;
                return;
            }
            if (data.winner === "draw") {
                statusEl.textContent = "🤝 It's a draw!";
                gameOver = true;
                thinking = false;
                return;
            }

            /* AI turn */
            statusEl.textContent = "AI is thinking…";
            await aiMove();
        } catch (err) {
            statusEl.textContent = "Error: " + err.message;
        }
        thinking = false;
    }

    /* ---- AI move ---- */
    async function aiMove() {
        const algorithm = algoSelect.value;
        const depth = parseInt(depthInput.value, 10);

        const res = await fetch("/api/move", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ board, algorithm, depth }),
        });
        const data = await res.json();
        if (data.error) { statusEl.textContent = data.error; return; }

        board = data.board;
        renderBoard();

        /* Draw tree */
        if (data.tree) drawTree(data.tree);

        if (data.winner === "ai") {
            statusEl.textContent = "🤖 AI wins!";
            gameOver = true;
            highlightWin(2);
            return;
        }
        if (data.winner === "draw") {
            statusEl.textContent = "🤝 It's a draw!";
            gameOver = true;
            return;
        }
        statusEl.textContent = "Your turn – click a column!";
    }

    /* ---- Helpers ---- */
    function isValidCol(col) {
        return col >= 0 && col < COLS && board[0][col] === 0;
    }

    function highlightWin(piece) {
        /* Simple: pulse all cells of the winning piece */
        const cells = boardEl.querySelectorAll(".cell");
        cells.forEach((c) => {
            if ((piece === 1 && c.classList.contains("player")) ||
                (piece === 2 && c.classList.contains("ai"))) {
                c.classList.add("win");
            }
        });
    }

    /* ---- Tree visualisation ---- */
    const NODE_R = 16;
    const H_GAP = 8;
    const V_GAP = 60;

    function countNodes(node) {
        if (!node) return 0;
        let count = 1;
        for (const c of (node.children || [])) count += countNodes(c);
        return count;
    }

    function layoutTree(node, depth) {
        /* Returns { node, x, y, width, children: [...] } */
        if (!node) return null;
        const kids = (node.children || []).map((c) => layoutTree(c, depth + 1));
        const childrenWidth = kids.reduce((s, k) => s + k.width, 0)
            + Math.max(0, kids.length - 1) * H_GAP;
        const myWidth = Math.max(NODE_R * 2 + 4, childrenWidth);

        return { node, depth, width: myWidth, kids };
    }

    function positionTree(layout, x, y) {
        layout.x = x + layout.width / 2;
        layout.y = y;
        let cx = x;
        for (const kid of layout.kids) {
            positionTree(kid, cx, y + V_GAP);
            cx += kid.width + H_GAP;
        }
    }

    function renderTreeSvg(layout, bestCol) {
        const total = countNodes(layout.node);
        treeStats.textContent = `(${total} node${total !== 1 ? "s" : ""})`;

        /* Limit rendering for very large trees */
        const MAX_RENDER = 600;
        let rendered = 0;

        const elements = [];

        function walk(lay) {
            if (rendered >= MAX_RENDER) return;
            rendered++;

            /* Edges */
            for (const kid of lay.kids) {
                if (rendered >= MAX_RENDER) break;
                const isBest = (lay.depth === 0 && kid.node.col === bestCol);
                elements.push(
                    `<line class="edge${isBest ? ' best' : ''}" x1="${lay.x}" y1="${lay.y}" x2="${kid.x}" y2="${kid.y}"/>`
                );
                walk(kid);
            }

            /* Node circle */
            let fill = "#334155";
            const t = lay.node.type;
            if (t === "max") fill = "#0ea5e9";
            else if (t === "min") fill = "#f43f5e";
            else if (t === "chance") fill = "#a855f7";
            else if (t === "pruned") fill = "#475569";
            else if (t === "leaf") fill = "#22c55e";
            elements.push(
                `<circle class="node-circle" cx="${lay.x}" cy="${lay.y}" r="${NODE_R}" fill="${fill}" stroke="#0f172a"/>`
            );

            /* Label */
            const label = lay.node.col !== null && lay.node.col !== undefined
                ? lay.node.col : "";
            elements.push(
                `<text class="node-label" x="${lay.x}" y="${lay.y}">${label}</text>`
            );

            /* Score below */
            const score = lay.node.score;
            const scoreText = typeof score === "number"
                ? (Math.abs(score) >= 1e8 ? (score > 0 ? "∞" : "-∞") : score)
                : (score || "");
            elements.push(
                `<text class="node-score" x="${lay.x}" y="${lay.y + NODE_R + 10}">${scoreText}</text>`
            );
        }

        walk(layout);

        const svgW = layout.width + 40;
        const maxDepth = findMaxDepth(layout);
        const svgH = maxDepth * V_GAP + NODE_R * 2 + 30;
        treeSvg.setAttribute("width", svgW);
        treeSvg.setAttribute("height", svgH);
        treeSvg.setAttribute("viewBox", `0 0 ${svgW} ${svgH}`);
        treeSvg.innerHTML = elements.join("\n");
    }

    function findMaxDepth(lay) {
        let d = 0;
        for (const kid of lay.kids) d = Math.max(d, findMaxDepth(kid));
        return d + 1;
    }

    function drawTree(tree) {
        if (!tree) { treeSvg.innerHTML = ""; treeStats.textContent = ""; return; }
        const layout = layoutTree(tree, 0);
        positionTree(layout, 20, NODE_R + 10);
        renderTreeSvg(layout, tree.col);
    }

    /* ---- Events ---- */
    depthInput.addEventListener("input", () => {
        depthValue.textContent = depthInput.value;
    });

    newGameBtn.addEventListener("click", initBoard);

    /* Start */
    initBoard();
})();
