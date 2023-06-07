"use strict";
window.addEventListener("load", main);
function main() {
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
