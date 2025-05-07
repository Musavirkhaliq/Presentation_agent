# FoldingDiff: Diffusion-Based Protein Backbone Generation and Sequence Design

---


# Introduction: Revolutionizing Protein Design with Diffusion Models

*   **The Protein Design Bottleneck:**
    *   Designing proteins with specific structures and functions is a major challenge.
    *   Traditional methods are slow, expensive, and often unsuccessful.

---

# Introduction: Revolutionizing Protein Design with Diffusion Models (Part 2)

*   **Introducing FoldingDiff: A Novel Solution**
    *   A cutting-edge pipeline leveraging diffusion models for *de novo* protein design.
    *   Integrates three powerful tools:
        *   **Diffusion Model:** Generates novel protein backbones.
        *   **ProteinMPNN:** Designs amino acid sequences that fit the backbones.
        *   **OmegaFold:** Predicts structure, validating the design.

*   **Our Innovative Approach**
    1.  **Generate:** Create diverse protein backbones using a learned diffusion process (learns from CATH dataset).
    2.  **Design:** Determine compatible amino acid sequences using ProteinMPNN.
    3.  **Validate:** Predict the 3D structure of the designed sequence with OmegaFold and assess self-consistency (TM-score).

---

# Introduction: Revolutionizing Protein Design with Diffusion Models (Part 3)

*   **Impact and Applications**
    *   Accelerate protein engineering for industrial and research applications.
    *   Revolutionize drug discovery by designing novel therapeutic proteins.
    *   Expand the possibilities of synthetic biology through custom-designed enzymes and biomaterials.

*Visual Suggestions:*

*   *A compelling graphic showing a protein structure transforming from noise to a well-defined shape (representing the diffusion process).*
*   *A flowchart illustrating the integrated pipeline: Diffusion Model -> ProteinMPNN -> OmegaFold -> Validation.*
*   *Images of potential applications: a drug molecule binding to a designed protein, a schematic of a synthetic biology application.*

---

# Representing Protein Structure: Dihedral Angles as a Language

*   **Protein Backbones: A Dihedral Language**

    *   Represented as a sequence of dihedral angles: φ (phi), ψ (psi), ω (omega), χ (chi) (for sidechains, not shown on every slide for simplicity).

        *   **Visual:** Show a simple diagram of a peptide bond highlighting the φ, ψ, and ω angles. Perhaps an abbreviated amino acid chain (e.g., Ala-Gly-Ser) highlighting the angles at the Glycine residue.
*   **Why Dihedrals?**

---

# Representing Protein Structure: Dihedral Angles as a Language (Part 2)

*   **Compact Representation:** Reduces dimensionality compared to Cartesian coordinates.
    *   **ML-Friendly:** Well-suited for machine learning algorithms.
    *   **Essential Information:** Captures key structural features of the protein backbone.

        *   **Visual:** A comparison of the amount of data needed to store dihedral angles compared to the cartesian coordinates. This could simply be a textual comparison "n * #_residues vs 3n * #_residues". N = number of values needed to store an angle.
*   **Data Preprocessing:** Preparing for the Model

---

# Representing Protein Structure: Dihedral Angles as a Language (Part 3)

*   **Normalization:** Angles mapped to the range [-π, π].
        *   *Example:* -3.5 rad becomes 2.78 rad.
    *   **Padding:** Sequences padded to a consistent length for batch processing.
        *   *Example:* Sequences of length 50 and 75 both padded to length 100.
    *   **Dataset Splitting:** Dividing data into training and validation sets.
        *   *Example:* 80% Training, 20% Validation (common split)

        *   **Visual:** A simple diagram illustrating sequence padding and dataset splitting.

---

# FoldingDiff: A Diffusion Model for Protein Backbone Generation

*   **FoldingDiff: Protein Backbone Generation via Diffusion**
    *   Generates novel protein backbones using a diffusion model.
    *   Inspired by image generation techniques adapted for protein structures.

*   **Forward Diffusion (Noising):**
    *   Gradually adds noise to protein dihedral angles (φ, ψ, ω).
    *   Transforms a valid protein structure into random noise over *T* timesteps.
    *   Example: Dihedral angles progressively deviate from their original values.
    *   Visual: Diagram showing protein structure evolving into noise.

---

# FoldingDiff: A Diffusion Model for Protein Backbone Generation (Part 2)

*   **Reverse Diffusion (Denoising):**
    *   Learns to reverse the noising process.
    *   Starts from random noise and iteratively denoises to reconstruct a protein backbone.
    *   Each denoising step refines the protein structure.
    *   Visual: Diagram showing random noise evolving into a protein structure.

---

# FoldingDiff: A Diffusion Model for Protein Backbone Generation (Part 3)

*   **Noise Schedules:**
    *   Control the rate of noise addition during forward diffusion.
    *   Examples:
        *   Linear: Constant rate of noise addition.
        *   Quadratic: Noise increases quadratically over time.
        *   Cosine: Noise follows a cosine function.
    *   Impact: Different schedules can affect the quality of generated structures.
    *   Visual: Graph comparing different noise schedules.

---

# FoldingDiff: A Diffusion Model for Protein Backbone Generation (Part 4)

*   **Model Architecture:**
    *   BERT-based Transformer.
    *   Captures long-range dependencies between amino acids in protein structures.
    *   Input: Sequence of dihedral angles.
    *   Output: Predicted change in dihedral angles during denoising.
    *   Visual: Simplified architecture diagram of the BERT-based Transformer.

---

# Sequence Design with ProteinMPNN: Fitting the Backbone

*   **ProteinMPNN: Sequence Design to Fit the Backbone**
    *   Powerful neural network for designing amino acid sequences.
    *   Ensures compatibility with a *given* protein backbone structure.
    *   Crucial step after FoldingDiff backbone generation.

*   **Sequence Design Process:**
    *   ProteinMPNN generates a sequence predicted to fold into the target backbone.
    *   Leverages the backbone generated by FoldingDiff.
    *   Sequence is then passed to OmegaFold for structure prediction and validation.

---

# Sequence Design with ProteinMPNN: Fitting the Backbone (Part 2)

*   **Energy-Based Model:**
    *   Employs an energy function to evaluate sequence-backbone compatibility.
    *   Lower energy implies higher probability of the sequence folding into the target backbone.
    *   A score will be produced to determine the folding probability.

---

# Sequence Design with ProteinMPNN: Fitting the Backbone (Part 3)

*   **Why ProteinMPNN?**
    *   Significantly faster and more accurate than traditional methods.
    *   Handles complex protein topologies.
    *   Key to realizing novel protein designs from FoldingDiff.
    *   Allows the generation of proteins not found in nature.

*   **Example Code Snippet** (Illustrative):
    ```bash
    # Run ProteinMPNN on FoldingDiff backbone (backbone.pdb)
    python run_proteinmpnn.py --pdb_path backbone.pdb --num_seq_per_target 1
    ```

**Visual Suggestions:**

---

# Sequence Design with ProteinMPNN: Fitting the Backbone (Part 4)

*   **Diagram:** Illustrate the overall workflow: FoldingDiff (backbone generation) -> ProteinMPNN (sequence design) -> OmegaFold (structure prediction/validation).
*   **Image:** Show a protein backbone alongside the designed amino acid sequence. Highlight specific residues and their interactions.
*   **Graph:** Display the energy landscape used by ProteinMPNN, showing how it identifies the optimal sequence.
*   **Animation:** A short animation showing a protein folding based on the ProteinMPNN-designed sequence.

---

# Structure Prediction with OmegaFold: Validating the Design

*   **OmegaFold: Structure Validation Powerhouse**
    *   State-of-the-art protein structure prediction model.
    *   Predicts 3D structure from amino acid sequence.

*   **Validation Process: Closing the Loop**
    *   ProteinMPNN designs sequence for generated backbone.
    *   OmegaFold predicts the structure of this designed sequence.

---

# Structure Prediction with OmegaFold: Validating the Design (Part 2)

*   **Self-Consistency is Key**
    *   Compare OmegaFold's predicted structure to the *original* generated backbone.
    *   **TM-score** quantifies structural similarity (e.g., TM-score > 0.7 indicates high similarity).
    *   High TM-score validates both the design & backbone generation process.

*   **Why This Matters**
    *   Confirms the designed sequence folds into the intended shape.
    *   Crucial for de novo protein design and engineering.
    *   Ensures the creation of new and functional proteins.

**Visual Suggestions:**

---

# Structure Prediction with OmegaFold: Validating the Design (Part 3)

*   **Left Side:** A visual representation of the protein design pipeline. The design pipeline should include: "Generated Backbone" -> "Designed Sequence (ProteinMPNN)" -> "Predicted Structure (OmegaFold)" -> "Comparison"
*   **Right Side:** Side-by-side comparison of:
    *   The generated backbone (e.g., cartoon representation).
    *   OmegaFold's predicted structure (same orientation, maybe different color).
*   **Bottom:** A TM-score scale visualization with an arrow pointing to 0.7, indicating a good score, and a short explanation of what is considered a good TM-score

---

# Evaluation Metrics: TM-Score for Self-Consistency

*   **TM-Score: Structural Similarity Metric**
    *   Quantifies the similarity between two protein structures.
    *   Ranges from 0 to 1, with higher values indicating greater similarity.

*   **Self-Consistency Evaluation**
    *   Assess the designed sequence's ability to fold back into the intended backbone.
    *   Calculate the TM-score between:
        *   **Original Backbone:** Generated by FoldingDiff.
        *   **Predicted Structure:** OmegaFold prediction from the designed sequence (ProteinMPNN).

---

# Evaluation Metrics: TM-Score for Self-Consistency (Part 2)

*   **Interpretation**
    *   **High TM-Score (e.g., > 0.7):** Successful design! The designed sequence folds into a structure closely resembling the original target backbone.
    *   **Low TM-Score:** Indicates potential issues with the designed sequence or backbone. The sequence may not fold into the desired conformation.

*   **Why Self-Consistency Matters**
    *   Validates the entire design pipeline (FoldingDiff + ProteinMPNN + OmegaFold).
    *   Filters out poorly designed sequences and backbones.
    *   Ensures that we are generating proteins with the desired structural properties.

**Visual Suggestions:**

---

# Evaluation Metrics: TM-Score for Self-Consistency (Part 3)

*   **Diagram:** Illustrate the self-consistency evaluation process: FoldingDiff → Backbone → ProteinMPNN → Sequence → OmegaFold → Predicted Structure → TM-score Comparison (Original Backbone vs. Predicted Structure). Arrows should clearly indicate the flow.
*   **Example Structures:** Show side-by-side comparison of an original backbone and a predicted structure with a high TM-score, highlighting the structural similarity. Also include another example with a lower TM-score to show the difference in quality.
*   **TM-Score Distribution:** A histogram showing the distribution of TM-scores obtained from multiple design iterations, demonstrating the overall performance of the pipeline.

---

# The Integrated Pipeline: From Noise to Design

## The Integrated Pipeline: From Noise to Design

*   **Automated Workflow: Noise $\rightarrow$ Structure $\rightarrow$ Sequence $\rightarrow$ Validation**
    *   Seamless integration of FoldingDiff, ProteinMPNN, and OmegaFold.
    *   Eliminates manual intervention, enabling high-throughput protein design.

*   **Ease of Use: Democratizing Protein Design**
    *   Designed for accessibility – streamlined input and output.
    *   Efficient protein design: From idea to validated structure in hours.
    *   Example: Simple command-line interface for pipeline execution.  `./run_pipeline.sh -input_seq example_seq.fasta` (Illustrative)

---

# The Integrated Pipeline: From Noise to Design (Part 2)

*   **Flexibility: Tailoring Designs to Your Needs**
    *   Adaptable to various design constraints and objectives (e.g., binding affinity, stability).
    *   Tunable parameters for custom noise schedules and sequence design criteria.
    *   Example: Setting TM-score thresholds for self-consistency evaluation. `TM-score > 0.7` (Target).

**(Visual Suggestions):**

*   **Workflow Diagram:** A clear diagram showing the flow from FoldingDiff (noise -> structure) to ProteinMPNN (sequence design) to OmegaFold (structure prediction) and a feedback loop for validation.
*   **Protein Structure Image:** A visually appealing image of a novel protein structure generated by the pipeline.
*   **Code Snippet:** A small, readable code snippet demonstrating a key step in the pipeline (e.g., calling ProteinMPNN).  (Abstracted)

---

# Conclusion: The Future of Protein Design

**Conclusion: The Future of Protein Design**

*   **Summary:** FoldingDiff: A powerful diffusion-based approach for generating novel protein structures *and* sequences.
    *   Generates diverse, plausible protein backbones.
    *   Designs sequences that fold into the generated structures.
    *   Addresses a key challenge in de novo protein design.

---

# Conclusion: The Future of Protein Design (Part 2)

*   **Potential Applications:** Expanding the protein universe
    *   **Drug Discovery:** Design novel binding proteins and therapeutic candidates. *[Visual: Image of a designed protein binding to a drug target]*
    *   **Enzyme Engineering:** Create enzymes with enhanced or novel catalytic activities. *[Visual: Diagram of an engineered enzyme catalyzing a reaction]*
    *   **Materials Science:** Develop new biomaterials with tailored properties. *[Visual: Illustration of a protein-based biomaterial]*
    *   **Synthetic Biology:** Construct novel biological systems with designed proteins. *[Visual: Schematic of a synthetic biological circuit]*

---

# Conclusion: The Future of Protein Design (Part 3)

*   **Future Directions:**
    *   **Improving the Model:**
        *   Explore different noise schedules (e.g., cosine annealing).
        *   Incorporate experimental data for enhanced realism.
    *   **Exploring New Applications:**
        *   Design proteins with specific functions or binding affinities.
        *   Address protein dynamics and flexibility.
    *   **Integrating Experimental Validation:** Essential to move beyond computational predictions. *[Visual: Image of a protein structure determined by X-ray crystallography or cryo-EM]*

---

# Conclusion: The Future of Protein Design (Part 4)

*   **Open Source:** FoldingDiff and associated tools are publicly available to promote collaboration and accelerate advancements.
    *   Contribute to improved models, expanded applications, and rigorous validation.
    *   [Link to Github Repository]

*   **Impact:** FoldingDiff offers the potential to revolutionize protein design, with broad implications across various scientific disciplines and industries.

---
