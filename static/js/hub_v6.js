/* ==========================================================
                    ZORO HUB V6
                CLEAN FRONTEND SYSTEM
========================================================== */

"use strict";


/* ==========================================================
                    DOM READY
========================================================== */

document.addEventListener("DOMContentLoaded", () => {

    initWelcomeModal();

    initMobileNavigation();

    initFeaturedSlider();

    initCardTilt();

    initSmoothNavigation();

    console.log("Zoro Hub V6 frontend loaded.");

});


/* ==========================================================
                    WELCOME MODAL
========================================================== */

function initWelcomeModal() {

    const overlay =
        document.getElementById("welcomeOverlay");

    const enterButton =
        document.getElementById("enterHub");


    if (!overlay || !enterButton) {
        return;
    }


    let hasSeenWelcome = false;


    try {

        hasSeenWelcome =
            localStorage.getItem(
                "zoroHubWelcomeSeen"
            ) === "true";

    } catch (error) {

        console.warn(
            "Zoro Hub could not access localStorage."
        );

    }


    if (!hasSeenWelcome) {

        overlay.hidden = false;

        document.body.classList.add(
            "welcome-open"
        );

    }


    enterButton.addEventListener(
        "click",
        () => {

            try {

                localStorage.setItem(
                    "zoroHubWelcomeSeen",
                    "true"
                );

            } catch (error) {

                console.warn(
                    "Could not save welcome state."
                );

            }


            overlay.hidden = true;

            document.body.classList.remove(
                "welcome-open"
            );

        }
    );


    /*
        Allow Escape to close the popup after
        the user has entered the Hub.
    */

    document.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Escape" &&
                !overlay.hidden
            ) {

                overlay.hidden = true;

                document.body.classList.remove(
                    "welcome-open"
                );

            }

        }
    );

}


/* ==========================================================
                    MOBILE NAVIGATION
========================================================== */

function initMobileNavigation() {

    const menuButton =
        document.getElementById("menuToggle");

    const nav =
        document.getElementById("navLinks");


    if (!menuButton || !nav) {
        return;
    }


    menuButton.addEventListener(
        "click",
        () => {

            const isOpen =
                nav.classList.toggle("open");

            menuButton.setAttribute(
                "aria-expanded",
                String(isOpen)
            );

        }
    );


    /*
        Close mobile navigation when clicking
        one of its links.
    */

    nav.querySelectorAll("a").forEach(
        (link) => {

            link.addEventListener(
                "click",
                () => {

                    nav.classList.remove("open");

                    menuButton.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }
            );

        }
    );


    /*
        Close when clicking outside.
    */

    document.addEventListener(
        "click",
        (event) => {

            if (
                !nav.contains(event.target) &&
                !menuButton.contains(event.target)
            ) {

                nav.classList.remove("open");

                menuButton.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }

        }
    );

}


/* ==========================================================
                    FEATURED SLIDER
========================================================== */

function initFeaturedSlider() {

    const slider =
        document.getElementById("heroSlider");


    if (!slider) {
        return;
    }


    const slides =
        Array.from(
            slider.querySelectorAll(
                ".hero-slide"
            )
        );


    const dots =
        Array.from(
            document.querySelectorAll(
                "#heroDots button"
            )
        );


    const nextButton =
        document.getElementById(
            "heroNext"
        );


    const previousButton =
        document.getElementById(
            "heroPrev"
        );


    if (!slides.length) {
        return;
    }


    let currentIndex = 0;

    let sliderTimer = null;

    let isHovered = false;

    let touchStartX = 0;

    let touchEndX = 0;


    const SLIDE_DELAY = 6500;

    const MIN_SWIPE_DISTANCE = 45;


    /* ======================================================
                        SHOW SLIDE
    ====================================================== */

    function showSlide(index) {

        if (index < 0) {

            index =
                slides.length - 1;

        }


        if (index >= slides.length) {

            index = 0;

        }


        currentIndex = index;


        slides.forEach(
            (slide, slideIndex) => {

                const active =
                    slideIndex === currentIndex;


                slide.classList.toggle(
                    "active",
                    active
                );


                slide.setAttribute(
                    "aria-hidden",
                    String(!active)
                );

            }
        );


        dots.forEach(
            (dot, dotIndex) => {

                const active =
                    dotIndex === currentIndex;


                dot.classList.toggle(
                    "active",
                    active
                );

            }
        );

    }


    /* ======================================================
                        NEXT / PREVIOUS
    ====================================================== */

    function nextSlide() {

        showSlide(
            currentIndex + 1
        );

    }


    function previousSlide() {

        showSlide(
            currentIndex - 1
        );

    }


    /* ======================================================
                        AUTO PLAY
    ====================================================== */

    function startAutoSlide() {

        stopAutoSlide();


        sliderTimer =
            window.setInterval(
                () => {

                    if (!isHovered) {

                        nextSlide();

                    }

                },
                SLIDE_DELAY
            );

    }


    function stopAutoSlide() {

        if (sliderTimer !== null) {

            window.clearInterval(
                sliderTimer
            );

            sliderTimer = null;

        }

    }


    /* ======================================================
                        BUTTONS
    ====================================================== */

    if (nextButton) {

        nextButton.addEventListener(
            "click",
            () => {

                nextSlide();

                startAutoSlide();

            }
        );

    }


    if (previousButton) {

        previousButton.addEventListener(
            "click",
            () => {

                previousSlide();

                startAutoSlide();

            }
        );

    }


    /* ======================================================
                        DOTS
    ====================================================== */

    dots.forEach(
        (dot, index) => {

            dot.addEventListener(
                "click",
                () => {

                    showSlide(index);

                    startAutoSlide();

                }
            );

        }
    );


    /* ======================================================
                        HOVER PAUSE
    ====================================================== */

    slider.addEventListener(
        "mouseenter",
        () => {

            isHovered = true;

        }
    );


    slider.addEventListener(
        "mouseleave",
        () => {

            isHovered = false;

        }
    );


    /* ======================================================
                        KEYBOARD
    ====================================================== */

    document.addEventListener(
        "keydown",
        (event) => {

            /*
                Don't hijack arrow keys while the user
                is interacting with an input or button.
            */

            const tag =
                event.target?.tagName;


            if (
                tag === "INPUT" ||
                tag === "TEXTAREA" ||
                tag === "SELECT"
            ) {

                return;

            }


            if (
                event.key === "ArrowRight"
            ) {

                nextSlide();

                startAutoSlide();

            }


            if (
                event.key === "ArrowLeft"
            ) {

                previousSlide();

                startAutoSlide();

            }

        }
    );


    /* ======================================================
                        TOUCH / SWIPE
    ====================================================== */

    slider.addEventListener(
        "touchstart",
        (event) => {

            const touch =
                event.changedTouches[0];


            if (!touch) {
                return;
            }


            touchStartX =
                touch.clientX;

        },
        { passive: true }
    );


    slider.addEventListener(
        "touchend",
        (event) => {

            const touch =
                event.changedTouches[0];


            if (!touch) {
                return;
            }


            touchEndX =
                touch.clientX;


            const distance =
                touchEndX -
                touchStartX;


            if (
                Math.abs(distance) <
                MIN_SWIPE_DISTANCE
            ) {

                return;

            }


            if (distance < 0) {

                nextSlide();

            } else {

                previousSlide();

            }


            startAutoSlide();

        },
        { passive: true }
    );


    /* ======================================================
                        INITIALIZE
    ====================================================== */

    showSlide(0);

    startAutoSlide();


    /*
        Respect reduced-motion preference.
    */

    const prefersReducedMotion =
        window.matchMedia &&
        window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;


    if (prefersReducedMotion) {

        stopAutoSlide();

    }

}


/* ==========================================================
                        CARD TILT
========================================================== */

function initCardTilt() {

    /*
        Only arcade cards.

        No old launcher/theme/achievement
        selectors anymore.
    */

    const cards =
        document.querySelectorAll(
            ".game-card"
        );


    if (!cards.length) {
        return;
    }


    const isTouchDevice =
        window.matchMedia &&
        window.matchMedia(
            "(pointer: coarse)"
        ).matches;


    if (isTouchDevice) {
        return;
    }


    cards.forEach(
        (card) => {

            card.addEventListener(
                "mousemove",
                (event) => {

                    const rect =
                        card.getBoundingClientRect();


                    if (
                        rect.width === 0 ||
                        rect.height === 0
                    ) {

                        return;

                    }


                    const x =
                        event.clientX -
                        rect.left;


                    const y =
                        event.clientY -
                        rect.top;


                    const percentX =
                        x / rect.width;


                    const percentY =
                        y / rect.height;


                    const rotateY =
                        (
                            percentX -
                            0.5
                        ) * 5;


                    const rotateX =
                        (
                            percentY -
                            0.5
                        ) * -5;


                    card.style.transform =
                        `
                        perspective(900px)
                        rotateX(${rotateX}deg)
                        rotateY(${rotateY}deg)
                        translateY(-5px)
                        `;

                }
            );


            card.addEventListener(
                "mouseleave",
                () => {

                    card.style.transform = "";

                }
            );

        }
    );

}


/* ==========================================================
                    SMOOTH NAVIGATION
========================================================== */

function initSmoothNavigation() {

    const links =
        document.querySelectorAll(
            'a[href^="#"]'
        );


    links.forEach(
        (link) => {

            link.addEventListener(
                "click",
                (event) => {

                    const href =
                        link.getAttribute(
                            "href"
                        );


                    if (
                        !href ||
                        href === "#"
                    ) {

                        return;

                    }


                    const target =
                        document.querySelector(
                            href
                        );


                    if (!target) {
                        return;
                    }


                    event.preventDefault();


                    target.scrollIntoView({
                        behavior:"smooth",
                        block:"start"
                    });

                }
            );

        }
    );

}


/* ==========================================================
                    PUBLIC ZORO HUB API
========================================================== */

/*
    These tiny helpers let future systems — such as
    rewards, achievements, analytics, favorites, etc. —
    interact with the Hub without rebuilding this file.
*/


window.ZoroHub = {

    goToSlide(index) {

        const slider =
            document.getElementById(
                "heroSlider"
            );


        if (!slider) {
            return;
        }


        const dots =
            document.querySelectorAll(
                "#heroDots button"
            );


        if (
            index < 0 ||
            index >= dots.length
        ) {

            return;

        }


        dots[index]?.click();

    },


    scrollToArcade() {

        document
            .getElementById("arcade")
            ?.scrollIntoView({
                behavior:"smooth",
                block:"start"
            });

    },


    resetWelcome() {

        try {

            localStorage.removeItem(
                "zoroHubWelcomeSeen"
            );

        } catch (error) {

            console.warn(
                "Could not reset welcome state."
            );

        }

    }

};