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
                    { img: "static/figures/dummy_gallery_image.png", link: "http://google.com" },
                    { img: "static/figures/dummy_gallery_image.png", link: "http://google.com" },
                    { img: "static/figures/dummy_gallery_image.png", link: "http://google.com" },
                ]
            },
            {
                label: "Pixel art",
                items: [
                    { img: "static/figures/dummy_gallery_image.png", link: "http://google.com" },
                    { img: "static/figures/dummy_gallery_image.png", link: "http://google.com" },
                    { img: "static/figures/dummy_gallery_image.png", link: "http://google.com" },
                ]
            },
            {
                label: "Impressionist style",
                items: [
                    { img: "static/figures/dummy_gallery_image.png", link: "http://google.com" },
                    { img: "static/figures/dummy_gallery_image.png", link: "http://google.com" },
                    { img: "static/figures/dummy_gallery_image.png", link: "http://google.com" },
                ]
            },
            {
                label: "Pencil sketch",
                items: [
                    { img: "static/figures/dummy_gallery_image.png", link: "http://google.com" },
                    { img: "static/figures/dummy_gallery_image.png", link: "http://google.com" },
                    { img: "static/figures/dummy_gallery_image.png", link: "http://google.com" },
                ]
            },
            // ... Add the other 2 groups here
        ]
    };

    // Configuration for Slide 2 (Physical Elements)
    // const physicalData = {
    //     title: "Physical Elements",
    //     groups: [
    //         {
    //             label: "Wood",
    //             items: [
    //                 { img: "static/figures/wood1.jpg", link: "#" },
    //                 { img: "static/figures/wood2.jpg", link: "#" },
    //                 { img: "static/figures/wood3.jpg", link: "#" }
    //             ]
    //         },
    //         // ... etc
    //     ]
    // };

    // --- 3. Execute Render ---
    renderGrid("slide-art-styles", artStylesData);
    // renderGrid("slide-physical-elements", physicalData);
});