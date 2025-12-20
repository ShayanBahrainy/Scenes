const MAX_QUALITY = {{max_quality}}

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
    if (num == 14) return "fourteen"
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
    video.classList = "video-player"
    video.autoplay = true
    video.preload = "metadata"
    video.playsInline = true
    video.oncontextmenu = () => (false);

    const background_video = document.createElement("video")
    background_video.classList = "background-player"
    background_video.autoplay = true
    background_video.preload = "metadata"
    background_video.playsInline = true
    background_video.oncontextmenu = () => (false);

    const video_frame = document.createElement("div")
    video_frame.classList = "video-frame fade-in"

    video_frame.appendChild(video)
    video_frame.appendChild(background_video)

    return video_frame
}

/**
 * 
 * @param {HTMLDivElement} videoFrame
 * @param {Number} segmentQuality
 * @param {Number} segmentIndex
 * @returns {Promise<Number>}
 */

function playSegment(videoFrame, segmentQuality, segmentIndex) {

    const players = videoFrame.children

    const videoSource = document.createElement("source")
    videoSource.src = `/video_${segmentQuality}_seg${segmentIndex}.webm`
    videoSource.type = "video/webm"

    for (const videoPlayer of players) {
        videoPlayer.innerHTML = ""
        videoPlayer.appendChild(videoSource.cloneNode())
    }

    videoSource.remove()

    let outerResolve

    let promise = new Promise(function (resolve, reject) {
        outerResolve = resolve
    })

    videoFrame.children[0].addEventListener("loadedmetadata", function (ev) {
        outerResolve(ev.target.duration)
    })

    return promise
}


let blockOut = 0

/**
 * 
 * @param {Number} currentQuality
 * @param {HTMLVideoElement} videoPlayer
 *
 * @returns {Number}
 */

function getQuality(currentQuality, videoPlayer) {
    let dropStats = videoPlayer.getVideoPlaybackQuality()
    const dropRatio = dropStats.droppedVideoFrames / dropStats.totalVideoFrames;

    if (dropRatio > 0.05 && currentQuality > 1) {
        currentQuality--;
        blockOut = 15;
    }
    else if (dropRatio < Math.pow(currentQuality + 1, -2) && currentQuality < MAX_QUALITY && blockOut <= 0) {
        currentQuality++;
    }
    console.log(`Dropping ${dropRatio * 100}% of frames.`)
    console.log(`Current Quality: ${currentQuality}`)

    return currentQuality;
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
    let currentQuality = 1

    let prev = null
    async function createTransition() {
        let video = createVideoPlayer()
        this.document.body.appendChild(video)

        if (prev) {
            prev.classList.toggle('fade-in')
            prev.classList.toggle('fade-out')
            prev.muted = true
            let toDelete = prev
            setTimeout(() => {
                toDelete.remove()
            }, 1000)
            currentQuality = getQuality(currentQuality, prev.children[0])
        }

        prev = video

        let duration = await playSegment(video, currentQuality, segmentIndex)
        segmentIndex++

        blockOut--;

        setTimeout(createTransition, Math.max(duration - 1, 0) * 1000)
    }

    createTransition()

})