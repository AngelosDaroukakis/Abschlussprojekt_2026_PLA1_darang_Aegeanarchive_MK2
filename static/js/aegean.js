const intro = document.getElementById("intro");
const enterButton = document.querySelector(".enter");
const canvas = document.getElementById("particles");

const INTRO_STORAGE_KEY = "aegeanIntroSeen";

let ctx;
let particles = [];
let burst = false;
let animationStarted = false;

function resizeCanvas() {
    if (!canvas) {
        return;
    }

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

function createParticles() {
    if (!canvas) {
        return;
    }

    particles = Array.from({ length: 190 }, () => {
        const angle = Math.random() * Math.PI * 2;
        const speed = Math.random() * 0.34 + 0.05;

        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            r: Math.random() * 1.9 + 0.35,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            a: Math.random() * 0.72 + 0.22,
        };
    });
}

function drawParticles() {
    if (!canvas || !ctx) {
        return;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (const particle of particles) {
        if (burst) {
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const dx = particle.x - centerX;
            const dy = particle.y - centerY;
            const distance = Math.sqrt(dx * dx + dy * dy) || 1;

            particle.vx += (dx / distance) * 0.056;
            particle.vy += (dy / distance) * 0.056;
            particle.a *= 0.994;
        }

        particle.x += particle.vx;
        particle.y += particle.vy;

        if (
            particle.x < -24 ||
            particle.x > canvas.width + 24 ||
            particle.y < -24 ||
            particle.y > canvas.height + 24
        ) {
            particle.x = Math.random() * canvas.width;
            particle.y = Math.random() * canvas.height;
            particle.a = Math.random() * 0.72 + 0.22;
        }

        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 231, 162, ${particle.a})`;
        ctx.fill();
    }

    requestAnimationFrame(drawParticles);
}

function markIntroAsSeen() {
    localStorage.setItem(INTRO_STORAGE_KEY, "true");
    document.documentElement.classList.add("intro-seen");
}

function showArchiveImmediately() {
    if (intro) {
        intro.classList.add("hide");
    }

    document.body.classList.remove("locked");
    document.body.classList.add("archive-open");
}

function openArchive() {
    if (!intro || intro.classList.contains("opening")) {
        return;
    }

    markIntroAsSeen();
    burst = true;
    intro.classList.add("opening");

    setTimeout(() => {
        intro.classList.add("hide");
        document.body.classList.remove("locked");
        document.body.classList.add("archive-open");
    }, 1260);
}

function startIntro() {
    if (!canvas || animationStarted) {
        return;
    }

    animationStarted = true;
    ctx = canvas.getContext("2d");
    resizeCanvas();
    createParticles();
    drawParticles();
}

if (intro) {
    intro.addEventListener("click", (event) => {
        event.stopPropagation();
    });
}

if (enterButton) {
    enterButton.addEventListener("click", (event) => {
        event.stopPropagation();
        openArchive();
    });
}

window.addEventListener("resize", () => {
    resizeCanvas();
    createParticles();
});

window.addEventListener("load", () => {
    const params = new URLSearchParams(window.location.search);
    const hasFilter =
        params.has("search") ||
        params.has("from") ||
        params.has("to");

    if (hasFilter || localStorage.getItem("aegeanIntroSeen") === "true") {
        showArchiveImmediately();
        return;
    }

    if (!intro) {
        showArchiveImmediately();
        return;
    }

    document.body.classList.add("locked");
    document.body.classList.remove("archive-open");
    startIntro();
});
