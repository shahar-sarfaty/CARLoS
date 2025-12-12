// static/js/gallery.js

document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. The Rendering Function ---
    function renderGrid(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return; // Skip if container doesn't exist on this page

        const groupsHtml = data.groups.map(group => {
            const imagesHtml = group.items.map((item, index) => `
                <div class="trio-item">
                    <span class="rank-number">#${index + 1}</span>
                    <a href="${item.link}" class="trio-link">
                        <img src="${item.img}" alt="${group.label} ${index + 1}">
                    </a>
                </div>
            `).join('');

            return `
                <div class="style-group">
                    <div class="trio-container">${imagesHtml}</div>
                    <p class="style-caption">${group.label}</p>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div class="art-styles-wrapper">
                <h2 class="main-headline">${data.title}</h2>
                <div class="styles-grid">${groupsHtml}</div>
            </div>
        `;
    }

    // --- 2. The Data Configurations ---
    
    // Configuration for Slide 1 (Art Styles)
    const artStylesData = {
        title: "Art Styles",
        groups: [
            {
                label: "Ink line art",
                items: [
                    { img: "static/figures/gallery_images/ink_line_art_1.png", link: "http://google.com" },
                    { img: "static/figures/gallery_images/ink_line_art_2.png", link: "http://google.com" },
                    { img: "static/figures/gallery_images/ink_line_art_3.png", link: "http://google.com" },
                ]
            },
            {
                label: "Pixel art",
                items: [
                    { img: "static/figures/gallery_images/pixel_art_1.png", link: "http://google.com" },
                    { img: "static/figures/gallery_images/pixel_art_2.png", link: "http://google.com" },
                    { img: "static/figures/gallery_images/pixel_art_3.png", link: "http://google.com" },
                ]
            },
            {
                label: "Impressionist style",
                items: [
                    { img: "static/figures/gallery_images/impressionist_1.png", link: "http://google.com" },
                    { img: "static/figures/gallery_images/impressionist_2.png", link: "http://google.com" },
                    { img: "static/figures/gallery_images/impressionist_3.png", link: "http://google.com" },
                ]
            },
            {
                label: "Pencil sketch",
                items: [
                    { img: "static/figures/gallery_images/pencil_sketch_1.png", link: "http://google.com" },
                    { img: "static/figures/gallery_images/pencil_sketch_2.png", link: "http://google.com" },
                    { img: "static/figures/gallery_images/pencil_sketch_3.png", link: "http://google.com" },
                ]
            },
        ]
    };

    // Configuration for Slide 2 (Physical Elements)
    const physicalData = {
        title: "Physical Elements",
        groups: [
            {
                label: "Foggy",
                items: [
                    { img: "static/figures/gallery_images/foggy_1.png", link: "#" },
                    { img: "static/figures/gallery_images/foggy_2.png", link: "#" },
                    { img: "static/figures/gallery_images/foggy_3.png", link: "#" }
                ]
            },
            {
                label: "Snowy",
                items: [
                    { img: "static/figures/gallery_images/snowy_1.png", link: "#" },
                    { img: "static/figures/gallery_images/snowy_2.png", link: "#" },
                    { img: "static/figures/gallery_images/snowy_3.png", link: "#" }
                ]
            },
            {
                label: "Dark clouds and lightning crackle in a stormy sky",
                items: [
                    { img: "static/figures/gallery_images/dark_clouds_1.png", link: "#" },
                    { img: "static/figures/gallery_images/dark_clouds_2.png", link: "#" },
                    { img: "static/figures/gallery_images/dark_clouds_3.png", link: "#" }
                ]
            },
            {
                label: "Light mist veils the landscape ethereally",
                items: [
                    { img: "static/figures/gallery_images/light_mist_1.png", link: "#" },
                    { img: "static/figures/gallery_images/light_mist_2.png", link: "#" },
                    { img: "static/figures/gallery_images/light_mist_3.png", link: "#" }
                ]
            },
        ]
    };

    // Configuration for Slide 3 (Cinematic and Lighting Effects)
    const cinematicData = {
        title: "Cinematic and Lighting Effects",
        groups: [
            {
                label: "Neon lighting",
                items: [
                    { img: "static/figures/gallery_images/neon_lighting_1.png", link: "#" },
                    { img: "static/figures/gallery_images/neon_lighting_2.png", link: "#" },
                    { img: "static/figures/gallery_images/neon_lighting_3.png", link: "#" }
                ]
            },
            {
                label: "Warm tones",
                items: [
                    { img: "static/figures/gallery_images/warm_tones_1.png", link: "#" },
                    { img: "static/figures/gallery_images/warm_tones_2.png", link: "#" },
                    { img: "static/figures/gallery_images/warm_tones_3.png", link: "#" }
                ]
            },
            {
                label: "Monochromatic",
                items: [
                    { img: "static/figures/gallery_images/monochromatic_1.png", link: "#" },
                    { img: "static/figures/gallery_images/monochromatic_2.png", link: "#" },
                    { img: "static/figures/gallery_images/monochromatic_3.png", link: "#" }
                ]
            },
            {
                label: "Blur backgrounds with shallow depth of field and creamy bokeh",
                items: [
                    { img: "static/figures/gallery_images/blur_background_1.png", link: "#" },
                    { img: "static/figures/gallery_images/blur_background_2.png", link: "#" },
                    { img: "static/figures/gallery_images/blur_background_3.png", link: "#" }
                ]
            },
        ]
    };

    // Configuration for Slide 4 (Semantic Shift)
    const semanticShiftData = {
        title: "Semantic Shift",
        groups: [
            {
                label: "Kimono",
                items: [
                    { img: "static/figures/gallery_images/kimono_1.png", link: "#" },
                    { img: "static/figures/gallery_images/kimono_2.png", link: "#" },
                    { img: "static/figures/gallery_images/kimono_3.png", link: "#" }
                ]
            },
            {
                label: "Surreal dreamlike",
                items: [
                    { img: "static/figures/gallery_images/surreal_dreamlike_1.png", link: "#" },
                    { img: "static/figures/gallery_images/surreal_dreamlike_2.png", link: "#" },
                    { img: "static/figures/gallery_images/surreal_dreamlike_3.png", link: "#" }
                ]
            },
            {
                label: "The elements are rendered in a grid of colored squares resembling retro video game graphics",
                items: [
                    { img: "static/figures/gallery_images/elements_rendered_1.png", link: "#" },
                    { img: "static/figures/gallery_images/elements_rendered_2.png", link: "#" },
                    { img: "static/figures/gallery_images/elements_rendered_3.png", link: "#" }
                ]
            },
            {
                label: "An image with an exceptionally high level of fine detail and texture",
                items: [
                    { img: "static/figures/gallery_images/high_details_1.png", link: "#" },
                    { img: "static/figures/gallery_images/high_details_2.png", link: "#" },
                    { img: "static/figures/gallery_images/high_details_3.png", link: "#" }
                ]
            },
        ]
    };

    // --- 3. Execute Render ---
    renderGrid("slide-art-styles", artStylesData);
    renderGrid("slide-physical-elements", physicalData);
    renderGrid("slide-cinematic-effects", cinematicData);
    renderGrid("slide-semantic-shifts", semanticShiftData);
});