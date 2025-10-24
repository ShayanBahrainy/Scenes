function updateClock(clock) {
    clock.innerText = generateText()
}

function getNumAsText(num) {
    if (num > 89) return "ninety" + (num % 10 > 0 ? '-'+getNumAsText(num % 10) : '')
    if (num > 79) return "eighty" + (num % 10 > 0 ? '-'+getNumAsText(num % 10) : '')
    if (num > 69) return "seventy" + (num % 10 > 0 ? '-'+getNumAsText(num % 10) : '')
    if (num > 59) return "sixty" + (num % 10 > 0 ? '-'+getNumAsText(num % 10) : '')
    if (num > 49) return "fifty" + (num % 10 > 0 ? '-'+getNumAsText(num % 10) : '')
    if (num > 39) return "forty" + (num % 10 > 0 ? '-'+getNumAsText(num % 10) : '')
    if (num > 29) return "thirty" + (num % 10 > 0 ? '-'+getNumAsText(num % 10) : '')
    if (num > 19) return "twenty" + (num % 10 > 0 ? '-'+getNumAsText(num % 10) : '')
    if (num == 19) return "nineteen"
    if (num == 18) return "eighteen"
    if (num == 17) return "seventeen"
    if (num == 16) return "sixteen"
    if (num == 15) return "fifteen"
    if (num == 14) return "forteen"
    if (num == 13) return "thirteen"
    if (num == 12) return "twelve"
    if (num == 11) return "eleven"
    if (num == 10) return "ten"
    if (num == 9) return "nine"
    if (num == 8) return "eight"
    if (num == 7) return "seven"
    if (num == 6) return "six"
    if (num == 5) return "five"
    if (num == 4) return "four"
    if (num == 3) return "three"
    if (num == 2) return "two"
    if (num == 1) return "one"
    if (num == 0) return "zero"
}

function generateText() {
    let hours = new Date().getHours()
    let minutes = new Date().getMinutes()
    let seconds = new Date().getSeconds()
    let milliseconds = new Date().getMilliseconds()


    return `${getNumAsText(hours)} hours, ${getNumAsText(minutes)} minutes`
}

window.addEventListener("load", function () {
    const hamburger = document.querySelector(".hamburger")
    const menu = this.document.querySelector(".menu")
    hamburger.addEventListener("click", function () {
        hamburger.classList.toggle("opened-hamburger")
        hamburger.classList.toggle("closed-hamburger")
        menu.classList.toggle("menu-opened")
        menu.classList.toggle("menu-closed")
    });

    const logoutmenu = this.document.querySelector(".logout-menu")
    logoutmenu?.addEventListener("change", function () {
        window.location = "/logout/" + logoutmenu.value
    })

    const subscribe = this.document.getElementById("subscribe")
    subscribe?.addEventListener("click", function () {
        location = "/why-subscribe"
    })

    const adminButton = this.document.getElementById("admin")
    adminButton?.addEventListener("click", function () {
        location = "/admin/dashboard"
    })

    const clock = this.document.querySelector(".clock")
    this.setInterval(updateClock, 1000, clock)
})