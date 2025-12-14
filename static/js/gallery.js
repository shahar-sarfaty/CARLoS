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
        title: "CARLoS Retrieval Examples - Art Styles",
        groups: [
            {
                label: "Ink line art",
                items: [
                    { img: "static/figures/gallery_images/ink_line_art_1.png", link: "https://civitai.com/models/136348?modelVersionId=150391" },
                    { img: "static/figures/gallery_images/ink_line_art_2.png", link: "https://civitai.com/models/178117?modelVersionId=200108" },
                    { img: "static/figures/gallery_images/ink_line_art_3.png", link: "https://civitai.com/models/120213/sdxl10-sketch-style-regulator-v1" },
                ]
            },
            {
                label: "Pixel art",
                items: [
                    { img: "static/figures/gallery_images/pixel_art_1.png", link: "https://civitai.com/models/235689/pixel-art-sliders-ntcaixyz" },
                    { img: "static/figures/gallery_images/pixel_art_2.png", link: "https://civitai.com/models/267667/16-bit-pixel-backgrounds-v2" },
                    { img: "static/figures/gallery_images/pixel_art_3.png", link: "https://civitai.com/models/144684/pixelartredmond-pixel-art-loras-for-sd-xl" },
                ]
            },
            {
                label: "Impressionist style",
                items: [
                    { img: "static/figures/gallery_images/impressionist_1.png", link: "https://civitai.com/models/160066/envy-anime-oil-xl-01" },
                    { img: "static/figures/gallery_images/impressionist_2.png", link: "https://civitai.com/models/118223/sdxloil-paintingoil-brush-stroke" },
                    { img: "static/figures/gallery_images/impressionist_3.png", link: "https://civitai.com/models/233083/watercolor-sliders-ntcaixyz" },
                ]
            },
            {
                label: "Pencil sketch",
                items: [
                    { img: "static/figures/gallery_images/pencil_sketch_1.png", link: "https://civitai.com/models/202764/anime-sketch-style-sdxl-and-sd15" },
                    { img: "static/figures/gallery_images/pencil_sketch_2.png", link: "https://civitai.com/models/120213/sdxl10-sketch-style-regulator-v1" },
                    { img: "static/figures/gallery_images/pencil_sketch_3.png", link: "https://civitai.com/models/132383/pe-pencil-drawing-style" },
                ]
            },
        ]
    };

    // Configuration for Slide 2 (Physical Elements)
    const physicalData = {
        title: "CARLoS Retrieval Examples - Physical Elements",
        groups: [
            {
                label: "Foggy",
                items: [
                    { img: "static/figures/gallery_images/foggy_1.png", link: "https://civitai.com/models/131060/fog-sdxl" },
                    { img: "static/figures/gallery_images/foggy_2.png", link: "https://civitai.com/models/136550/rpgwraithxl" },
                    { img: "static/figures/gallery_images/foggy_3.png", link: "https://civitai.com/models/241901/storm-cloud-style-sdxl-sd-15" }
                ]
            },
            {
                label: "Snowy",
                items: [
                    { img: "static/figures/gallery_images/snowy_1.png", link: "https://civitai.com/models/237531/aether-snow-lora-for-sdxl" },
                    { img: "static/figures/gallery_images/snowy_2.png", link: "https://civitai.com/models/228846/sdxl-snow-style" },
                    { img: "static/figures/gallery_images/snowy_3.png", link: "https://civitai.com/models/136484/pe-snow-sculpture-style" }
                ]
            },
            {
                label: "Dark clouds and lightning crackle in a stormy sky",
                items: [
                    { img: "static/figures/gallery_images/dark_clouds_1.png", link: "https://civitai.com/models/241901/storm-cloud-style-sdxl-sd-15" },
                    { img: "static/figures/gallery_images/dark_clouds_2.png", link: "https://civitai.com/models/141029/aether-cloud-lora-for-sdxl" },
                    { img: "static/figures/gallery_images/dark_clouds_3.png", link: "https://civitai.com/models/158990/sdxlsacredbeast" }
                ]
            },
            {
                label: "Light mist veils the landscape ethereally",
                items: [
                    { img: "static/figures/gallery_images/light_mist_1.png", link: "https://civitai.com/models/132942/rpgghostxl" },
                    { img: "static/figures/gallery_images/light_mist_2.png", link: "https://civitai.com/models/245889?modelVersionId=277389" },
                    { img: "static/figures/gallery_images/light_mist_3.png", link: "https://civitai.com/models/134856?modelVersionId=148554" }
                ]
            },
        ]
    };

    // Configuration for Slide 3 (Cinematic and Lighting Effects)
    const cinematicData = {
        title: "CARLoS Retrieval Examples - Cinematic and Lighting Effects",
        groups: [
            {
                label: "Neon lighting",
                items: [
                    { img: "static/figures/gallery_images/neon_lighting_1.png", link: "https://civitai.com/models/134643/blacklight-makeup-sdxl-lora" },
                    { img: "static/figures/gallery_images/neon_lighting_2.png", link: "https://civitai.com/models/269931/neon-style-xl" },
                    { img: "static/figures/gallery_images/neon_lighting_3.png", link: "https://civitai.com/models/137160/pe-neon-sign-style" }
                ]
            },
            {
                label: "Warm tones",
                items: [
                    { img: "static/figures/gallery_images/warm_tones_1.png", link: "https://civitai.com/models/235319/amber-style-lora-15sdxl" },
                    { img: "static/figures/gallery_images/warm_tones_2.png", link: "https://civitai.com/models/231860/golden-glory-sdxl-lora" },
                    { img: "static/figures/gallery_images/warm_tones_3.png", link: "https://civitai.com/models/63072?modelVersionId=153680" }
                ]
            },
            {
                label: "Monochromatic",
                items: [
                    { img: "static/figures/gallery_images/monochromatic_1.png", link: "https://civitai.com/models/120213/sdxl10-sketch-style-regulator-v1" },
                    { img: "static/figures/gallery_images/monochromatic_2.png", link: "https://civitai.com/models/127018/lineaniredmond-linear-manga-style-for-sd-xl-anime-style" },
                    { img: "static/figures/gallery_images/monochromatic_3.png", link: "https://civitai.com/models/126450/only-black-sdxl" }
                ]
            },
            {
                label: "Blur backgrounds with shallow depth of field and creamy bokeh",
                items: [
                    { img: "static/figures/gallery_images/blur_background_1.png", link: "https://civitai.com/models/141517/xlfeltcraft" },
                    { img: "static/figures/gallery_images/blur_background_2.png", link: "https://civitai.com/models/138619/sdxlsewingdoll" },
                    { img: "static/figures/gallery_images/blur_background_3.png", link: "https://civitai.com/models/380539/zavys-rimlight-sdxl" }
                ]
            },
        ]
    };

    // Configuration for Slide 4 (Semantic Shift)
    const semanticShiftData = {
        title: "CARLoS Retrieval Examples - Semantic Shift",
        groups: [
            {
                label: "Kimono",
                items: [
                    { img: "static/figures/gallery_images/kimono_1.png", link: "https://civitai.com/models/120206/sdxlchinese-style-illustration" },
                    { img: "static/figures/gallery_images/kimono_2.png", link: "https://civitai.com/models/73822?modelVersionId=324867" },
                    { img: "static/figures/gallery_images/kimono_3.png", link: "https://civitai.com/models/120283/hanfu-tang-sdxl-sdxl" }
                ]
            },
            {
                label: "Surreal dreamlike",
                items: [
                    { img: "static/figures/gallery_images/surreal_dreamlike_1.png", link: "https://civitai.com/models/228963/sdxl-aurora" },
                    { img: "static/figures/gallery_images/surreal_dreamlike_2.png", link: "https://civitai.com/models/234208?modelVersionId=264081" },
                    { img: "static/figures/gallery_images/surreal_dreamlike_3.png", link: "https://civitai.com/models/245889?modelVersionId=277389" }
                ]
            },
            {
                label: "The elements are rendered in a grid of colored squares resembling retro video game graphics",
                items: [
                    { img: "static/figures/gallery_images/elements_rendered_1.png", link: "https://civitai.com/models/235689/pixel-art-sliders-ntcaixyz" },
                    { img: "static/figures/gallery_images/elements_rendered_2.png", link: "https://civitai.com/models/267667/16-bit-pixel-backgrounds-v2" },
                    { img: "static/figures/gallery_images/elements_rendered_3.png", link: "https://civitai.com/models/130190?modelVersionId=142815" }
                ]
            },
            {
                label: "An image with an exceptionally high level of fine detail and texture",
                items: [
                    { img: "static/figures/gallery_images/high_details_1.png", link: "https://civitai.com/models/269592?modelVersionId=303921" },
                    { img: "static/figures/gallery_images/high_details_2.png", link: "#https://civitai.com/models/470073?modelVersionId=560995" },
                    { img: "static/figures/gallery_images/high_details_3.png", link: "https://civitai.com/models/134614/pe-epic-land-style-landscapes" }
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