// import { foo, bar } from "...";

window.addEventListener("load", main);

// var globalVarA = null;
// var globalVarB = null;
// var globalVarC = null;

function main() {
  initializeMagicText(3, 1000);
  initializeCommandSnippets();
}

// ============== \\
// MAIN FUNCTIONS \\
function initializeMagicText(numStarsPerText: number, starAnimInterval: number) {
  initializeMagicStars(numStarsPerText, starAnimInterval);
  window.onfocus = () => initializeMagicStars(numStarsPerText, starAnimInterval);
}

function initializeMagicStars(numStarsPerText: number, starAnimInterval: number) {
  const magicStars = document.querySelectorAll(".magic-star");
  magicStars.forEach(star => star.remove());

  const magicTextElems = document.querySelectorAll(".magic-text");
  magicTextElems.forEach(elem => {
    // For each text element, we want to create
    // the desired number of stars and start their
    // animation loops.

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

function animateStar(star: HTMLElement) {
  star.style.setProperty("--star-left", `${randInt(-10, 110)}%`);
  star.style.setProperty("--star-top", `${randInt(5, 95)}%`);

  // DOM Reflow
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

// ================ \\
// COMMAND SNIPPETS \\

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

// ======================== \\
// GENERAL HELPER FUNCTIONS \\
// ======================== \\

function randInt(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getCookieValue(key: string) {
  const value = document.cookie
    .split("; ")
    .find((row) => row.startsWith(key + "="))
    ?.split("=")[1];
  return value;
}

function setCookieValue(key: string, value: any, age?: number) {
  age = age || 31536000;
  const cookie = `${key}=${value}; max-age=${age}; SameSite=None; path=/; Secure`;
  document.cookie = cookie;
}