// import { foo, bar } from "...";

window.addEventListener("load", main);

// var globalVarA = null;
// var globalVarB = null;
// var globalVarC = null;
var seedRandom = mulberry32(9);

function main() {
  console.log("test");
  addAnimationObserver();
  initializeStarCanvas();
  initializeMagicText(3, 1000);
  initializeCommandSnippets();

  // The scroll top button should work even without js enabled so it uses
  // an anchor, however that appends an ugly has to the url so this prevents that.
  const scrollButtons = document.querySelectorAll('[href*="scroll-to-top"]');
  scrollButtons.forEach(scrollButton => {
    scrollButton.addEventListener("click", (evt) => {
      window.scrollTo({ top: 0, behavior: "smooth" });
      evt.preventDefault();
    });
  });
}

// ============ \\
//  MAGIC TEXT  \\

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

// ========================== \\
// STARRY BACKGROUND & CANVAS \\

interface star {
  x: number, // int postition
  y: number, // int position

  maxr: number, // float maximum radius
  minr: number, // float minimum radius
  dr: number, // radius changing velocity
  r: number, // float current radius

  brightness: number, // 0-1 brightness value
}

function initializeStarCanvas() {
  const canvas = document.getElementById("star-canvas") as HTMLCanvasElement;
  const context = canvas.getContext("2d");

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  let numStars = Math.round((window.innerWidth + window.innerHeight) / 10);
  let stars = createRandomStars(numStars, canvas.width, canvas.height);
  drawAllStars(context, stars);

  addEventListener("resize", () => {
    seedRandom = mulberry32(9); // Reset the seeded random number generator
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

  // TODO: use this instead of set interval??
  // requestAnimationFrame(function anim(t) {
  //   if (w !== innerWidth) w = canvas.width = innerWidth;
  //   if (h !== innerHeight) h = canvas.height = innerHeight;
  //   ctx.fillStyle = "#100";
  //   drawCircle(5, 9, w * 10);
  //   ctx.fillStyle = ctx.strokeStyle = "#fff";
  //   t /= 1000
  //   stars.forEach(stars => stars.tick(t))
  //   requestAnimationFrame(anim);
  // });
}

function clearCanvas(context: CanvasRenderingContext2D, canvas: HTMLCanvasElement) {
  context.beginPath();
  context.closePath();
  context.clearRect(0, 0, canvas.width, canvas.height);
}

function drawCircle(ctx: CanvasRenderingContext2D, x: number, y: number, r: number, color: string) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.ellipse(x, y, r, r, 0, 0, Math.PI * 2);
  ctx.fill();
}

function createRandomStars(numStars: number, maxWidth: number, maxHeight: number) {
  const stars: star[] = []; // TODO: make star fade anim duration randomized
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

function drawAllStars(ctx: CanvasRenderingContext2D, stars: star[]) {
  stars.forEach(star => {
    const color = addOpacityToHexColor(star.brightness, "#ffffff");
    drawCircle(ctx, star.x, star.y, star.r, color);
  });
}

function updateAllStars(stars: star[]) {
  stars.forEach(star => {
    star.r += star.dr;
    if ((star.r + star.dr > star.maxr) || (star.r + star.dr < star.minr)) {
      star.dr *= -1;
    }
  });
}

// ==================== \\
// ON SCROLL ANIMATIONS \\

/**
 * Creates an intersection observer which triggers animations for
 * some elements when they scroll onto the page by modifying their class.
 */
function addAnimationObserver() {
  const animatedItems = document.querySelectorAll(".animated-item");
  animatedItems.forEach(item => item.classList.add("pre-anim"));

  const options = {
    // @ts-ignore
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

// ======================== \\
// GENERAL HELPER FUNCTIONS \\
// ======================== \\

function randInt(min: number, max: number, seeded?: boolean) {
  const randFunc = seeded ? seedRandom : Math.random;
  return Math.floor(randFunc() * (max - min + 1)) + min;
}

function randNum(min: number, max: number, seeded?: boolean) {
  const randFunc = seeded ? seedRandom : Math.random;
  return (randFunc() * (max - min)) + min;
}

// Returns a seeded pseudorandom number generator.
function mulberry32(a: any) {
  return function () {
    var t = a += 0x6D2B79F5;
    t = Math.imul(t ^ t >>> 15, t | 1);
    t ^= t + Math.imul(t ^ t >>> 7, t | 61);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  }
}

function addOpacityToHexColor(opacity: number, hexColor: string) {
  if (hexColor.length !== 7) throw new TypeError("hexColor must be a 6-digit string with the pound sign!");

  // Convert opacity to a two-digit hexadecimal value
  const opacityHex = Math.round(opacity * 255).toString(16).padStart(2, '0');
  return hexColor + opacityHex;
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