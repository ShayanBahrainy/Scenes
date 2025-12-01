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

function createVideoPlayer() {
    const video = document.createElement("video")
    video.classList = "fade-in video-player"
    video.autoplay = true

    const video_frame = document.createElement("div")
    video_frame.classList = "video-frame"

    video_frame.appendChild(video)

    return video_frame
}

function playSegment(videoFrame, segmentIndex) {

    const videoPlayer = videoFrame.children[0]

    let resolveOuter
    function saveResolve(resolve) {
        resolveOuter = resolve
    }
    let promise = new Promise(saveResolve)

    let mediaSource = new MediaSource()

    videoPlayer.src = URL.createObjectURL(mediaSource)

    mediaSource.addEventListener("sourceopen", () => {
        const videoBuffer = mediaSource.addSourceBuffer('video/webm codecs="vp9"')
        const audioBuffer = mediaSource.addSourceBuffer('audio/webm codecs="vorbis')

        Promise.all([
            fetch(`/video_4_seg${segmentIndex}.webm`).then(r => r.arrayBuffer()),
            fetch(`/audio_seg${segmentIndex}.webm`).then(r => r.arrayBuffer())
        ]).then(([videoData, audioData]) => {
            videoBuffer.appendBuffer(videoData)
            audioBuffer.appendBuffer(audioData)
            videoBuffer.addEventListener("updateend", function a() {

                resolveOuter(mediaSource)

                videoBuffer.removeEventListener("updateend", a)
            })
        }).catch(err => {
                console.error("Failed to fetch segment", segmentIndex, err)
        })
    })
    return promise
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
    updateClock(clock)
    this.setInterval(updateClock, 1000 * 10, clock)

    let segmentIndex = 0

    let prev = null
    async function createTransition() {
        let video = createVideoPlayer()
        this.document.body.appendChild(video)
        let mediaSource = await playSegment(video, segmentIndex)
        segmentIndex++
        if (prev) {
            prev.classList.toggle('fade-in')
            prev.classList.toggle('fade-out')
            prev.muted = true
            let toDelete = prev
            setTimeout(() => {
                toDelete.src = ""
                toDelete.remove()
            }, 1000)
        }
        prev = video
        setTimeout(createTransition, (mediaSource.duration * 1000) - 1000)
    }

    createTransition()

})