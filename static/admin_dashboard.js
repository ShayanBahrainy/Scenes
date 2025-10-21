window.addEventListener("DOMContentLoaded", function () {
    let bar1 = document.querySelector(".not-subscribed")
    let bar2 = document.querySelector(".subscribed")

    let val1 = bar1.getAttribute("data-value")
    let val2 = bar2.getAttribute("data-value")

    if (val1 < val2) {
        bar1.classList.toggle("switch-right")
        bar2.classList.toggle("switch-left")
    }

    if (val1 == val2) {
        bar1.classList.toggle("equalize-bar")
        bar2.classList.toggle("equalize-bar")
    }

    this.document.querySelector(".upload-button").addEventListener("click", function() {
        window.location = "/admin/upload"
    })

    this.document.querySelector(".drafts-button").addEventListener("click", function() {
        window.location = "/admin/drafts"
    })

    this.document.querySelector(".published-button").addEventListener("click", function() {
        window.location = "/admin/published"
    })

    this.document.querySelector(".email-dashboard").addEventListener("click", function () {
        window.location = "/admin/email_dashboard"
    })
})