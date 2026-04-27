// CyberHygiene Project - Interactive Features

document.addEventListener('DOMContentLoaded', function() {

    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('.nav-links a, .footer-section a[href^="#"]');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Only handle internal links (starting with #)
            if (href.startsWith('#')) {
                e.preventDefault();
                const targetId = href.substring(1);
                const targetSection = document.getElementById(targetId);

                if (targetSection) {
                    const headerOffset = 80; // Account for sticky header
                    const elementPosition = targetSection.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Add active state to navigation based on scroll position
    const sections = document.querySelectorAll('section[id]');
    const navItems = document.querySelectorAll('.nav-links a');

    function updateActiveNavLink() {
        let currentSection = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.pageYOffset >= (sectionTop - 200)) {
                currentSection = section.getAttribute('id');
            }
        });

        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === '#' + currentSection) {
                item.classList.add('active');
            }
        });
    }

    // Update on scroll
    window.addEventListener('scroll', updateActiveNavLink);

    // Animate metrics on scroll into view
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');

                // Animate numbers if they have the stat-number or metric-value class
                if (entry.target.classList.contains('stat') ||
                    entry.target.classList.contains('metric')) {
                    animateNumber(entry.target);
                }
            }
        });
    }, observerOptions);

    // Observe stat and metric elements
    const stats = document.querySelectorAll('.stat, .metric, .compliance-card');
    stats.forEach(stat => observer.observe(stat));

    // Animate numbers counting up
    function animateNumber(element) {
        const numberElement = element.querySelector('.stat-number, .metric-value, .compliance-status');
        if (!numberElement) return;

        const finalValue = numberElement.textContent.trim();
        const isPercentage = finalValue.includes('%');
        const numericValue = parseInt(finalValue.replace(/\D/g, ''));

        if (isNaN(numericValue)) return;

        let currentValue = 0;
        const increment = Math.ceil(numericValue / 50); // Adjust speed
        const duration = 1000; // 1 second
        const stepTime = duration / (numericValue / increment);

        const counter = setInterval(() => {
            currentValue += increment;
            if (currentValue >= numericValue) {
                currentValue = numericValue;
                clearInterval(counter);
            }
            numberElement.textContent = isPercentage ? currentValue + '%' : currentValue;
        }, stepTime);
    }

    // Mobile menu toggle (if needed in future)
    const menuToggle = document.querySelector('.menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            const navLinks = document.querySelector('.nav-links');
            navLinks.classList.toggle('mobile-active');
        });
    }

    // Add fade-in animation to cards on scroll
    const cards = document.querySelectorAll('.card, .tech-category');
    const cardObserver = new IntersectionObserver(function(entries) {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100); // Stagger animation
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        cardObserver.observe(card);
    });

    // Print event listeners
    window.addEventListener('beforeprint', function() {
        console.log('Preparing document for printing...');
    });

    // Add current year to footer if needed
    const yearElements = document.querySelectorAll('.current-year');
    const currentYear = new Date().getFullYear();
    yearElements.forEach(el => {
        el.textContent = currentYear;
    });

    // Log page load for analytics (placeholder)
    console.log('CyberHygiene Project website loaded successfully');
    console.log('System Status: Operational');
    console.log('Compliance Level: 100% NIST 800-171');
});

// Scroll to top functionality
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Show/hide scroll to top button
window.addEventListener('scroll', function() {
    const scrollButton = document.querySelector('.scroll-to-top');
    if (scrollButton) {
        if (window.pageYOffset > 300) {
            scrollButton.classList.add('visible');
        } else {
            scrollButton.classList.remove('visible');
        }
    }
});
