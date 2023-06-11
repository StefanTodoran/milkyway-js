"use strict";
window.addEventListener("load", main);
var seedRandom = mulberry32(9);
function main() {
    addAnimationObserver();
    initializeStarCanvas();
    initializeMagicText(3, 1000);
    initializeCommandSnippets();
    const scrollButton = document.getElementById("scroll-top-button");
    scrollButton.addEventListener("click", (evt) => {
        window.scrollTo({ top: 0, behavior: "smooth" });
        evt.preventDefault();
    });
}
function initializeMagicText(numStarsPerText, starAnimInterval) {
    initializeMagicStars(numStarsPerText, starAnimInterval);
    window.onfocus = () => initializeMagicStars(numStarsPerText, starAnimInterval);
}
function initializeMagicStars(numStarsPerText, starAnimInterval) {
    const magicStars = document.querySelectorAll(".magic-star");
    magicStars.forEach(star => star.remove());
    const magicTextElems = document.querySelectorAll(".magic-text");
    magicTextElems.forEach(elem => {
        for (let i = 0; i < numStarsPerText; i++) {
            setTimeout(() => {
                const star = createMagicStar();
                elem.appendChild(star);
                animateStar(star);
                setInterval(() => animateStar(star), starAnimInterval);
            }, i * (starAnimInterval / numStarsPerText));
        }
    });
}
function animateStar(star) {
    star.style.setProperty("--star-left", `${randInt(-10, 110)}%`);
    star.style.setProperty("--star-top", `${randInt(5, 95)}%`);
    star.style.animation = "none";
    star.offsetHeight;
    star.style.animation = "";
}
function createMagicStar() {
    const star = document.createElement("img");
    star.classList.add("magic-star");
    star.src = "assets/star.svg";
    return star;
}
function initializeCommandSnippets() {
    const commandSnippets = document.querySelectorAll(".command-snippet");
    commandSnippets.forEach(snippet => {
        const content = snippet.textContent;
        snippet.addEventListener("click", () => {
            navigator.clipboard.writeText(content);
            snippet.classList.add("active");
            setTimeout(() => snippet.classList.remove("active"), 1000);
        });
    });
}
function initializeStarCanvas() {
    const canvas = document.getElementById("star-canvas");
    const context = canvas.getContext("2d");
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    let numStars = Math.round((window.innerWidth + window.innerHeight) / 10);
    let stars = createRandomStars(numStars, canvas.width, canvas.height);
    drawAllStars(context, stars);
    addEventListener("resize", () => {
        seedRandom = mulberry32(9);
        numStars = Math.round((window.innerWidth + window.innerHeight) / 10);
        stars = createRandomStars(numStars, canvas.width, canvas.height);
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        drawAllStars(context, stars);
    });
    setInterval(() => {
        updateAllStars(stars);
        clearCanvas(context, canvas);
        drawAllStars(context, stars);
    }, 1);
}
function clearCanvas(context, canvas) {
    context.beginPath();
    context.closePath();
    context.clearRect(0, 0, canvas.width, canvas.height);
}
function drawCircle(ctx, x, y, r, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.ellipse(x, y, r, r, 0, 0, Math.PI * 2);
    ctx.fill();
}
function createRandomStars(numStars, maxWidth, maxHeight) {
    const stars = [];
    for (let i = 0; i < numStars; i++) {
        const sizeA = randNum(0.1, 2, true);
        const sizeB = randNum(0.1, 2, true);
        stars.push({
            x: randInt(0, maxWidth, true),
            y: randInt(0, maxHeight, true),
            maxr: Math.max(sizeA, sizeB),
            minr: Math.min(sizeA, sizeB),
            dr: Math.abs(sizeA - sizeB) / 100,
            r: (sizeA + sizeB) / 2,
            brightness: randNum(0, 1, true),
        });
    }
    return stars;
}
function drawAllStars(ctx, stars) {
    stars.forEach(star => {
        const color = addOpacityToHexColor(star.brightness, "#ffffff");
        drawCircle(ctx, star.x, star.y, star.r, color);
    });
}
function updateAllStars(stars) {
    stars.forEach(star => {
        star.r += star.dr;
        if ((star.r + star.dr > star.maxr) || (star.r + star.dr < star.minr)) {
            star.dr *= -1;
        }
    });
}
function addAnimationObserver() {
    const animatedItems = document.querySelectorAll(".animated-item");
    animatedItems.forEach(item => item.classList.add("pre-anim"));
    const options = {
        root: null,
        rootMargin: "0px",
        threshold: 0.45
    };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.remove("pre-anim");
            }
        });
    }, options);
    animatedItems.forEach((element) => observer.observe(element));
}
function randInt(min, max, seeded) {
    const randFunc = seeded ? seedRandom : Math.random;
    return Math.floor(randFunc() * (max - min + 1)) + min;
}
function randNum(min, max, seeded) {
    const randFunc = seeded ? seedRandom : Math.random;
    return (randFunc() * (max - min)) + min;
}
function mulberry32(a) {
    return function () {
        var t = a += 0x6D2B79F5;
        t = Math.imul(t ^ t >>> 15, t | 1);
        t ^= t + Math.imul(t ^ t >>> 7, t | 61);
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
}
function addOpacityToHexColor(opacity, hexColor) {
    if (hexColor.length !== 7)
        throw new TypeError("hexColor must be a 6-digit string with the pound sign!");
    const opacityHex = Math.round(opacity * 255).toString(16).padStart(2, '0');
    return hexColor + opacityHex;
}
function getCookieValue(key) {
    var _a;
    const value = (_a = document.cookie
        .split("; ")
        .find((row) => row.startsWith(key + "="))) === null || _a === void 0 ? void 0 : _a.split("=")[1];
    return value;
}
function setCookieValue(key, value, age) {
    age = age || 31536000;
    const cookie = `${key}=${value}; max-age=${age}; SameSite=None; path=/; Secure`;
    document.cookie = cookie;
}
