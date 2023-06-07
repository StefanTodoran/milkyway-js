// import { foo, bar } from "...";

window.addEventListener("load", main);

// var globalVarA = null;
// var globalVarB = null;
// var globalVarC = null;

function main() {

}

// ================ \\
// HELPER FUNCTIONS \\
// ================ \\



// ========================= \\
// STORED COOKIE PREFERENCES \\
// ========================= \\

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