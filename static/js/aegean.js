(() => {
    "use strict";

    const root = document.documentElement;
    const body = document.body;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const finePointer = window.matchMedia("(pointer: fine)").matches;

    const qs = (selector, scope = document) => scope.querySelector(selector);
    const qsa = (selector, scope = document) => [...scope.querySelectorAll(selector)];

    const showToast = (message) => {
        const toast = qs("[data-ui-toast]");
        if (!toast) return;
        toast.textContent = message;
        toast.classList.add("is-visible");
        window.clearTimeout(showToast.timeout);
        showToast.timeout = window.setTimeout(() => toast.classList.remove("is-visible"), 2400);
    };

    function setupIntro() {
        const intro = qs("#intro");
        if (!intro) {
            body.classList.remove("locked");
            body.classList.add("archive-open");
            return;
        }

        const finish = () => {
            intro.classList.add("is-finished");
            body.classList.remove("locked");
            body.classList.add("archive-open");
            try { localStorage.setItem("aegeanIntroSeen", "true"); } catch (error) { /* ignore */ }
            window.setTimeout(() => intro.remove(), 500);
        };

        const open = () => {
            if (intro.classList.contains("is-opening")) return;
            intro.classList.add("is-opening");
            window.setTimeout(finish, reduceMotion ? 40 : 1450);
        };

        if (root.classList.contains("intro-seen")) {
            finish();
            return;
        }

        qs(".enter-button", intro)?.addEventListener("click", open);
        qs("[data-intro-skip]", intro)?.addEventListener("click", open);
    }

    function setupReveal() {
        const items = qsa(".reveal, .reveal-card");
        if (!items.length) return;

        if (reduceMotion || !("IntersectionObserver" in window)) {
            items.forEach((item) => item.classList.add("is-visible"));
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.12, rootMargin: "0px 0px -7% 0px" });

        items.forEach((item, index) => {
            item.style.transitionDelay = `${Math.min(index % 5, 4) * 70}ms`;
            observer.observe(item);
        });
    }

    function setupHeaderAndTop() {
        const header = qs("[data-site-header]");
        const topButton = qs("[data-back-to-top]");
        const mobileTop = qs("[data-back-to-top-mobile]");
        let scheduled = false;

        const update = () => {
            const y = window.scrollY;
            header?.classList.toggle("is-scrolled", y > 18);
            topButton?.classList.toggle("is-visible", y > 700);
            scheduled = false;
        };

        window.addEventListener("scroll", () => {
            if (scheduled) return;
            scheduled = true;
            requestAnimationFrame(update);
        }, { passive: true });

        const goTop = () => window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
        topButton?.addEventListener("click", goTop);
        mobileTop?.addEventListener("click", goTop);
        update();
    }

    function setupActiveNavigation() {
        const links = qsa("[data-nav-target]");
        if (!links.length || !("IntersectionObserver" in window)) return;

        const sections = links.map((link) => qs(`#${link.dataset.navTarget}`)).filter(Boolean);
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                links.forEach((link) => link.classList.toggle("is-active", link.dataset.navTarget === entry.target.id));
            });
        }, { rootMargin: "-35% 0px -55% 0px", threshold: 0 });

        sections.forEach((section) => observer.observe(section));
    }

    function setupSearchShortcut() {
        const input = qs("#search-input");
        if (!input) return;
        document.addEventListener("keydown", (event) => {
            const tag = document.activeElement?.tagName;
            const typing = tag === "INPUT" || tag === "TEXTAREA" || document.activeElement?.isContentEditable;
            if (event.key === "/" && !typing) {
                event.preventDefault();
                input.focus();
                input.select();
            }
        });
    }

    function setupMagnetic() {
        if (reduceMotion || !finePointer) return;
        qsa("[data-magnetic]").forEach((element) => {
            element.addEventListener("pointermove", (event) => {
                const rect = element.getBoundingClientRect();
                const x = event.clientX - rect.left - rect.width / 2;
                const y = event.clientY - rect.top - rect.height / 2;
                element.style.transform = `translate3d(${x * .13}px, ${y * .13}px, 0)`;
            });
            element.addEventListener("pointerleave", () => { element.style.transform = "translate3d(0,0,0)"; });
        });
    }

    function setupTilt() {
        if (reduceMotion || !finePointer) return;
        qsa("[data-tilt]").forEach((element) => {
            const max = element.classList.contains("detail-marble-frame") ? 1.1 : 2;
            element.addEventListener("pointermove", (event) => {
                const rect = element.getBoundingClientRect();
                const x = (event.clientX - rect.left) / rect.width - .5;
                const y = (event.clientY - rect.top) / rect.height - .5;
                element.style.transform = `perspective(1300px) rotateX(${y * -max * 2}deg) rotateY(${x * max * 2}deg)`;
            });
            element.addEventListener("pointerleave", () => { element.style.transform = "perspective(1300px) rotateX(0) rotateY(0)"; });
        });
    }

    function setupParallax() {
        if (reduceMotion || !finePointer) return;
        qsa("[data-parallax-root]").forEach((rootElement) => {
            const targets = qsa("[data-parallax]", rootElement);
            if (!targets.length) return;
            rootElement.addEventListener("pointermove", (event) => {
                const rect = rootElement.getBoundingClientRect();
                const x = (event.clientX - rect.left) / rect.width - .5;
                const y = (event.clientY - rect.top) / rect.height - .5;
                targets.forEach((target) => {
                    const strength = Number.parseFloat(target.dataset.parallax || ".2");
                    target.style.transform = `translate3d(${x * 34 * strength}px, ${y * 34 * strength}px, 0)`;
                });
            });
            rootElement.addEventListener("pointerleave", () => targets.forEach((target) => { target.style.transform = "translate3d(0,0,0)"; }));
        });
    }

    
    function setupTransitions() {
        if (reduceMotion) return;
        qsa("[data-transition-link]").forEach((link) => {
            link.addEventListener("click", (event) => {
                if (event.metaKey || event.ctrlKey || event.shiftKey || link.target === "_blank") return;
                const url = new URL(link.href, window.location.href);
                const sameAnchor = url.pathname === location.pathname && url.search === location.search && url.hash;
                if (sameAnchor) return;
                event.preventDefault();
                body.classList.add("is-transitioning");
                window.setTimeout(() => { location.href = link.href; }, 680);
            });
        });
    }

    function setupImages() {
        qsa(".gallery-image-shell img, .detail-image-shell img, .hero-frame img").forEach((image) => {
            const done = () => image.classList.add("is-loaded");
            if (image.complete && image.naturalWidth > 0) done();
            else image.addEventListener("load", done, { once: true });
        });
    }

    function setupGalleryViews() {
        const gallery = qs("[data-gallery]");
        const buttons = qsa("[data-gallery-view]");
        if (!gallery || !buttons.length) return;

        let view = "mosaic";
        try { view = localStorage.getItem("aegeanGalleryView") || "mosaic"; } catch (error) { /* ignore */ }
        if (!buttons.some((button) => button.dataset.galleryView === view)) view = "mosaic";

        const apply = (next) => {
            gallery.style.opacity = ".35";
            window.setTimeout(() => {
                gallery.dataset.view = next;
                buttons.forEach((button) => {
                    const active = button.dataset.galleryView === next;
                    button.classList.toggle("is-active", active);
                    button.setAttribute("aria-pressed", String(active));
                });
                gallery.style.opacity = "1";
            }, reduceMotion ? 0 : 160);
        };

        apply(view);
        buttons.forEach((button) => button.addEventListener("click", () => {
            view = button.dataset.galleryView;
            apply(view);
            try { localStorage.setItem("aegeanGalleryView", view); } catch (error) { /* ignore */ }
        }));
    }

    function setupCharacterCount() {
        const textarea = qs("#description");
        const counter = qs("[data-character-count]");
        if (!textarea || !counter) return;
        const update = () => { counter.textContent = `${textarea.value.length} / ${textarea.maxLength}`; };
        textarea.addEventListener("input", update);
        update();
    }

    function setupDeleteConfirmation() {
        qsa("[data-confirm-delete]").forEach((button) => button.addEventListener("click", (event) => {
            if (!window.confirm("Beschreibung wirklich löschen?")) event.preventDefault();
        }));
    }

    function setupCopyLink() {
        const button = qs("[data-copy-link]");
        if (!button) return;
        button.addEventListener("click", async () => {
            try {
                await navigator.clipboard.writeText(location.href);
                showToast("Link kopiert");
            } catch (error) {
                showToast("Link konnte nicht kopiert werden");
            }
        });
    }

    function setupFocusViewer() {
        const viewer = qs("[data-focus-viewer]");
        if (!viewer) return;
        const image = qs("[data-focus-image]", viewer);
        const openButtons = qsa("[data-focus-open]");
        const closeButtons = qsa("[data-focus-close]", viewer);
        const source = openButtons.find((button) => button.dataset.focusSrc)?.dataset.focusSrc;

        const open = () => {
            if (source && image && !image.src) image.src = source;
            viewer.classList.add("is-open");
            viewer.setAttribute("aria-hidden", "false");
            body.classList.add("focus-open");
        };

        const close = () => {
            viewer.classList.remove("is-open");
            viewer.setAttribute("aria-hidden", "true");
            body.classList.remove("focus-open");
        };

        openButtons.forEach((button) => button.addEventListener("click", open));
        closeButtons.forEach((button) => button.addEventListener("click", close));
        image?.addEventListener("load", () => image.classList.add("is-loaded"), { once: true });
        document.addEventListener("keydown", (event) => { if (event.key === "Escape" && viewer.classList.contains("is-open")) close(); });
    }

    function setupFlashDismiss() {
        qsa(".flash-message").forEach((message, index) => window.setTimeout(() => {
            message.style.opacity = "0";
            message.style.transform = "translateY(-8px)";
            window.setTimeout(() => message.remove(), 380);
        }, 4200 + index * 350));
    }

    function setupCountUp() {
        qsa("[data-count-up]").forEach((element) => {
            const end = Number.parseInt(element.dataset.countUp || "0", 10);
            if (reduceMotion || !Number.isFinite(end) || end <= 0) return;
            const start = performance.now();
            const duration = 900;
            const tick = (now) => {
                const progress = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                element.textContent = String(Math.round(end * eased));
                if (progress < 1) requestAnimationFrame(tick);
            };
            requestAnimationFrame(tick);
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        setupIntro();
        setupReveal();
        setupHeaderAndTop();
        setupActiveNavigation();
        setupSearchShortcut();
        setupMagnetic();
        setupTilt();
        setupParallax();
        setupPointerLight();
        setupTransitions();
        setupImages();
        setupGalleryViews();
        setupCharacterCount();
        setupDeleteConfirmation();
        setupCopyLink();
        setupFocusViewer();
        setupFlashDismiss();
        setupCountUp();
    });
})();
