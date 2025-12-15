# CARLoS: Retrieval via Concise Assessment Representation of LoRAs at Scale

**Authors:** Shahar Sarfaty, Adi Haviv, Uri Y. Hacohen, Niva Elkin-Koren, Roi Livni, Amit H. Bermano

[![arXiv](https://img.shields.io/badge/arXiv-[2512.08826]-b31b1b.svg)](https://arxiv.org/abs/2512.08826)
[![Website](https://img.shields.io/badge/Website-Project_Page-blue)](https://shahar-sarfaty.github.io/CARLoS/)

---

## 🚧 Code Release Status

**The code for this project is currently being organized and cleaned up.** We are planning to release the source code and data soon.

Please **Star ⭐** and **Watch 👁️** this repository to receive a notification when the code is released.

---

## Abstract

The rapid proliferation of generative components, such as LoRAs, has created a vast but unstructured ecosystem. Existing discovery methods depend on unreliable user descriptions or biased popularity metrics, hindering usability. We present CARLoS, a large-scale framework for characterizing LoRAs without requiring additional metadata. Analyzing over 650 LoRAs, we employ them in image generation over a variety of prompts and seeds, as a credible way to assess their behavior. Using CLIP embeddings and their difference to a base-model generation, we concisely define a three-part representation: Directions, defining semantic shift; Strength, quantifying the significance of the effect; and Consistency, quantifying how stable the effect is. Using these representations, we develop an efficient retrieval framework that semantically matches textual queries to relevant LoRAs while filtering overly strong or unstable ones, outperforming textual baselines in automated and human evaluations. While retrieval is our primary focus, the same representation also supports analyses linking Strength and Consistency to legal notions of substantiality and volition, key considerations in copyright, positioning CARLoS as a practical system with broader relevance for LoRA analysis.

## Citation

If you find our work helpful, please cite it as:

```bibtex
@misc{sarfaty2025carlosretrievalconciseassessment,
      title={CARLoS: Retrieval via Concise Assessment Representation of LoRAs at Scale}, 
      author={Shahar Sarfaty and Adi Haviv and Uri Hacohen and Niva Elkin-Koren and Roi Livni and Amit H. Bermano},
      year={2025},
      eprint={2512.08826},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2512.08826}, 
    }