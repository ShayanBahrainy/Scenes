window.addEventListener('load', function() {
    const retry = this.document.querySelector('.retry-button')

    if (retry) {
        retry.addEventListener('click', function() {
            const params = new URLSearchParams(window.location.search)
            const session_id = params.get('session_id')

            if (!session_id) {
                console.error('No session_id found in URL parameters.')
                return
            }

            fetch('/reuse-checkout-session?session=' + session_id).then(async function(response){
                if (!response.ok) {
                    location = '/subscribe'
                }
                window.location = '/subscribe?reuse_secret=' + await response.text()
            })
        })
    }

    else {
        const continue_button = this.document.querySelector('.continue-button')

        continue_button.addEventListener('click', function() {
            continue_button.classList.toggle('move-out')
            document.querySelector('.main-content').classList.toggle('move-out')
            document.querySelector('.info-line').classList.toggle('move-out')
            setTimeout(function() {
                window.location = '/'
            }, 1.5 * 1000)
        })
    }
})