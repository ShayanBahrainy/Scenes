window.addEventListener('DOMContentLoaded', function() {
    const subscribe = this.document.querySelector('.subscribe-button')

    subscribe.addEventListener('click', function() {
        window.location.href = '/subscribe'
    })
})