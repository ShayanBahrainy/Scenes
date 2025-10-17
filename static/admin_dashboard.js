window.addEventListener("DOMContentLoaded", function () {
    let bar1 = document.querySelector(".not-subscribed")
    let bar2 = document.querySelector(".subscribed")

    let val1 = bar1.getAttribute("data-value")
    let val2 = bar2.getAttribute("data-value")

    if (val2 > val1) {
        bar1.classList.toggle("switch-right")
        bar2.classList.toggle("switch-left")
    }
    if (val1 == val2) {
        bar1.classList.toggle("equalize")
        bar2.classList.toggle("equalize")
    }
})