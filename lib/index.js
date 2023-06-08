"use strict";
window.addEventListener("load", main);
function main() {
    console.log("Starting website...");
    initializeMagicText(3, 1000);
    initializeCommandSnippets();
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
function randInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
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
