// static/js/comparison.js

document.addEventListener('DOMContentLoaded', () => {

    function renderComparison(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // 1. Build Header Row
        let gridContent = `
            <div class="grid-header">#1</div>
            <div class="grid-header">#2</div>
            <div class="grid-header">#3</div>
            <div></div> `;

        // 2. Build Rows
        data.rows.forEach(row => {
            row.images.forEach((imgObj, index) => {
                gridContent += `
                    <a href="${imgObj.link}" class="comp-link">
                        <img src="${imgObj.src}" alt="${row.method} ${index + 1}">
                    </a>
                `;
            });
            gridContent += `<div class="method-label">${row.method}</div>`;
        });

        // 3. Add Title INSIDE the grid (New Step)
        // This allows CSS to position it strictly under the images
        gridContent += `<div class="comp-category-title">${data.title}</div>`;

        // 4. Assemble Full HTML
        container.innerHTML = `
            <div class="comparison-wrapper">
                <div class="source-panel">
                    <div class="source-label-top">${data.sourceLabel}</div>
                    <img src="${data.sourceImage}" class="source-img" alt="Source">
                    <p class="source-prompt">"${data.sourcePrompt}"</p>
                </div>

                <div class="results-panel">
                    <div class="comparison-grid">
                        ${gridContent}
                    </div>
                    </div>
            </div>
        `;
    }

    // ... (Rest of your data configuration remains the same) ...

    // --- DATA CONFIGURATION ---

    // 1. Pixel Art Data
    const pixelArtData = {
        title: "Pixel art",
        sourceLabel: "SDXL",
        sourceImage: "static/figures/comparison_images/sdxl_vanilla.png", // You need to create this image
        sourcePrompt: "A mom holding a baby",
        rows: [
            {
                method: "CARLoS",
                images: [
                    { src: "static/figures/comparison_images/pixel_carlos_1.png", link: "https://civitai.com/models/235689/pixel-art-sliders-ntcaixyz" },
                    { src: "static/figures/comparison_images/pixel_carlos_2.png", link: "https://civitai.com/models/267667/16-bit-pixel-backgrounds-v2" },
                    { src: "static/figures/comparison_images/pixel_carlos_3.png", link: "https://civitai.com/models/144684/pixelartredmond-pixel-art-loras-for-sd-xl" }
                ]
            },
            {
                method: "QWEN 3",
                images: [
                    { src: "static/figures/comparison_images/pixel_textuals_1.png", link: "https://civitai.com/models/144684/pixelartredmond-pixel-art-loras-for-sd-xl" },
                    { src: "static/figures/comparison_images/pixel_textuals_2.png", link: "https://civitai.com/models/114334/pixel-art-sdxl-rw" },
                    { src: "static/figures/comparison_images/pixel_textuals_3.png", link: "https://civitai.com/models/235689/pixel-art-sliders-ntcaixyz" }
                ]
            },
            {
                method: "E5",
                images: [
                    { src: "static/figures/comparison_images/pixel_textuals_1.png", link: "https://civitai.com/models/144684/pixelartredmond-pixel-art-loras-for-sd-xl" },
                    { src: "static/figures/comparison_images/pixel_textuals_2.png", link: "https://civitai.com/models/114334/pixel-art-sdxl-rw" },
                    { src: "static/figures/comparison_images/pixel_textuals_3.png", link: "https://civitai.com/models/235689/pixel-art-sliders-ntcaixyz" }
                ]
            },
            {
                method: "GTE",
                images: [
                    { src: "static/figures/comparison_images/pixel_textuals_1.png", link: "https://civitai.com/models/144684/pixelartredmond-pixel-art-loras-for-sd-xl" },
                    { src: "static/figures/comparison_images/pixel_textuals_2.png", link: "https://civitai.com/models/114334/pixel-art-sdxl-rw" },
                    { src: "static/figures/comparison_images/pixel_textuals_3.png", link: "https://civitai.com/models/235689/pixel-art-sliders-ntcaixyz" }
                ]
            },
            {
                method: "BGE",
                images: [
                    { src: "static/figures/comparison_images/pixel_textuals_1.png", link: "https://civitai.com/models/144684/pixelartredmond-pixel-art-loras-for-sd-xl" },
                    { src: "static/figures/comparison_images/pixel_textuals_2.png", link: "https://civitai.com/models/114334/pixel-art-sdxl-rw" },
                    { src: "static/figures/comparison_images/pixel_textuals_3.png", link: "https://civitai.com/models/235689/pixel-art-sliders-ntcaixyz" }
                ]
            }
        ]
    };
    
    // 1. Low key lighting Data
    const lowKeyLightingData = {
        title: "Low key lighting",
        sourceLabel: "SDXL",
        sourceImage: "static/figures/comparison_images/sdxl_vanilla.png", // You need to create this image
        sourcePrompt: "A mom holding a baby",
        rows: [
            {
                method: "CARLoS",
                images: [
                    { src: "static/figures/comparison_images/low_key_carlos_1.png", link: "https://civitai.com/models/295530/zavys-dark-atmospheric-contrast-sdxl" },
                    { src: "static/figures/comparison_images/low_key_carlos_2.png", link: "https://civitai.com/models/633300/dark-dramatic-chiaroscuro-lighting-slidersntcaixyz-notrigger" },
                    { src: "static/figures/comparison_images/low_key_carlos_3.png", link: "https://civitai.com/models/126450/only-black-sdxl" }
                ]
            },
            {
                method: "QWEN 3",
                images: [
                    { src: "static/figures/comparison_images/low_key_qwen_1.png", link: "https://civitai.com/models/295530/zavys-dark-atmospheric-contrast-sdxl" },
                    { src: "static/figures/comparison_images/low_key_qwen_2.png", link: "https://civitai.com/models/633300/dark-dramatic-chiaroscuro-lighting-slidersntcaixyz-notrigger" },
                    { src: "static/figures/comparison_images/low_key_qwen_3.png", link: "https://civitai.com/models/134643/blacklight-makeup-sdxl-lora" }
                ]
            },
            {
                method: "E5",
                images: [
                    { src: "static/figures/comparison_images/low_key_e5_1.png", link: "https://civitai.com/models/206979/kk-or-radiant-darkness-sdxl" },
                    { src: "static/figures/comparison_images/low_key_e5_2.png", link: "https://civitai.com/models/228974/great-lighting-slidersntcaixyz" },
                    { src: "static/figures/comparison_images/low_key_e5_3.png", link: "https://civitai.com/models/190243/liminal-space-style" }
                ]
            },
            {
                method: "GTE",
                images: [
                    { src: "static/figures/comparison_images/low_key_gte_1.png", link: "https://civitai.com/models/245943/bio-luminescence" },
                    { src: "static/figures/comparison_images/low_key_gte_2.png", link: "https://civitai.com/models/190243/liminal-space-style" },
                    { src: "static/figures/comparison_images/low_key_gte_3.png", link: "https://civitai.com/models/131818/soap-photo-enhancer-for-sdxl-shot-on-a-phone" }
                ]
            },
            {
                method: "BGE",
                images: [
                    { src: "static/figures/comparison_images/low_key_bge_1.png", link: "https://civitai.com/models/295530/zavys-dark-atmospheric-contrast-sdxl" },
                    { src: "static/figures/comparison_images/low_key_bge_2.png", link: "https://civitai.com/models/36561/neon-night" },
                    { src: "static/figures/comparison_images/low_key_bge_3.png", link: "https://civitai.com/models/118223/sdxloil-paintingoil-brush-stroke" }
                ]
            }
        ]
    };
    
    // 1. Celestial being Data
    const celestialBeingData = {
        title: "A character that looks like a celestial being, made of stars, nebulae, and cosmic dust.",
        sourceLabel: "SDXL",
        sourceImage: "static/figures/comparison_images/sdxl_vanilla.png", // You need to create this image
        sourcePrompt: "A mom holding a baby",
        rows: [
            {
                method: "CARLoS",
                images: [
                    { src: "static/figures/comparison_images/celestial_carlos_1.png", link: "https://civitai.com/models/228963/sdxl-aurora" },
                    { src: "static/figures/comparison_images/celestial_carlos_2.png", link: "https://civitai.com/models/310235/glowneon-xl-lora" },
                    { src: "static/figures/comparison_images/celestial_carlos_3.png", link: "https://civitai.com/models/168414/wizardcoreai-sdxl-sd15-konyconi" }
                ]
            },
            {
                method: "QWEN 3",
                images: [
                    { src: "static/figures/comparison_images/celestial_qwen_1.png", link: "https://civitai.com/models/149635?modelVersionId=167154" },
                    { src: "static/figures/comparison_images/celestial_qwen_2.png", link: "https://civitai.com/models/149635?modelVersionId=176918" },
                    { src: "static/figures/comparison_images/celestial_qwen_3.png", link: "https://civitai.com/models/170630/donm-demon-characters-sdxl" }
                ]
            },
            {
                method: "E5",
                images: [
                    { src: "static/figures/comparison_images/celestial_e5_1.png", link: "https://civitai.com/models/118831?modelVersionId=148734" },
                    { src: "static/figures/comparison_images/celestial_e5_2.png", link: "https://civitai.com/models/225984?modelVersionId=254934" },
                    { src: "static/figures/comparison_images/celestial_e5_3.png", link: "https://civitai.com/models/131060/fog-sdxl" }
                ]
            },
            {
                method: "GTE",
                images: [
                    { src: "static/figures/comparison_images/celestial_gte_1.png", link: "https://civitai.com/models/125246/deathburger-xl" },
                    { src: "static/figures/comparison_images/celestial_gte_2.png", link: "https://civitai.com/models/137160/pe-neon-sign-style" },
                    { src: "static/figures/comparison_images/celestial_gte_3.png", link: "https://civitai.com/models/263222/aerith-gainsborough-final-fantasy-vii-sdxl-lora" }
                ]
            },
            {
                method: "BGE",
                images: [
                    { src: "static/figures/comparison_images/celestial_bge_1.png", link: "https://civitai.com/models/128247/sdxl-yuanorlets-get-some-mecha-elements" },
                    { src: "static/figures/comparison_images/celestial_bge_2.png", link: "https://civitai.com/models/137897/by-night-portraits" },
                    { src: "static/figures/comparison_images/celestial_bge_3.png", link: "https://civitai.com/models/124747?modelVersionId=372096" }
                ]
            }
        ]
    };

    // 1. Detailed futuristic scene Data
    const detailedFuturisticSceneData = {
        title: "A detailed, futuristic scene with the vibrant neon and gritty realism of the game Cyberpunk 2077.",
        sourceLabel: "SDXL",
        sourceImage: "static/figures/comparison_images/sdxl_vanilla.png", // You need to create this image
        sourcePrompt: "A mom holding a baby",
        rows: [
            {
                method: "CARLoS",
                images: [
                    { src: "static/figures/comparison_images/detailed_carlos_1.png", link: "https://civitai.com/models/244479/dark-futuristic-circuit-boards" },
                    { src: "static/figures/comparison_images/detailed_carlos_2.png", link: "https://civitai.com/models/269931/neon-style-xl" },
                    { src: "static/figures/comparison_images/detailed_carlos_3.png", link: "https://civitai.com/models/133621/lah-cyberpunk-or-sdxl" }
                ]
            },
            {
                method: "QWEN 3",
                images: [
                    { src: "static/figures/comparison_images/detailed_qwen_1.png", link: "https://civitai.com/models/102838?modelVersionId=141343" },
                    { src: "static/figures/comparison_images/detailed_qwen_2.png", link: "https://civitai.com/models/133621/lah-cyberpunk-or-sdxl" },
                    { src: "static/figures/comparison_images/detailed_qwen_3.png", link: "https://civitai.com/models/128568?modelVersionId=141094" }
                ]
            },
            {
                method: "E5",
                images: [
                    { src: "static/figures/comparison_images/detailed_e5_1.png", link: "https://civitai.com/models/128568?modelVersionId=141094" },
                    { src: "static/figures/comparison_images/detailed_e5_2.png", link: "https://civitai.com/models/102838?modelVersionId=141343" },
                    { src: "static/figures/comparison_images/detailed_e5_3.png", link: "https://civitai.com/models/135492/cyberpunk-style-sci-fi-lora-xl" }
                ]
            },
            {
                method: "GTE",
                images: [
                    { src: "static/figures/comparison_images/detailed_gte_1.png", link: "https://civitai.com/models/102838?modelVersionId=141343" },
                    { src: "static/figures/comparison_images/detailed_gte_2.png", link: "https://civitai.com/models/128568?modelVersionId=141094" },
                    { src: "static/figures/comparison_images/detailed_gte_3.png", link: "https://civitai.com/models/310235/glowneon-xl-lora" }
                ]
            },
            {
                method: "BGE",
                images: [
                    { src: "static/figures/comparison_images/detailed_bge_1.png", link: "https://civitai.com/models/102838?modelVersionId=141343" },
                    { src: "static/figures/comparison_images/detailed_bge_2.png", link: "https://civitai.com/models/128247/sdxl-yuanorlets-get-some-mecha-elements" },
                    { src: "static/figures/comparison_images/detailed_bge_3.png", link: "https://civitai.com/models/257148?modelVersionId=289968" }
                ]
            }
        ]
    };

    // --- EXECUTE ---
    renderComparison("comp-slide-pixel-art", pixelArtData);
    renderComparison("comp-slide-low-key", lowKeyLightingData);
    renderComparison("comp-slide-futuristic", detailedFuturisticSceneData);
    renderComparison("comp-slide-celestial", celestialBeingData);
    
    // Note: Create similar data objects for Celestial, Futuristic, etc.
    // renderComparison("comp-slide-celestial", celestialData);
    // renderComparison("comp-slide-futuristic", futuristicData);
    // renderComparison("comp-slide-low-key", lowKeyData);

});