# ViEmoSpeech — Presentation Speaker Script

**Presentation:** `ViEmoSpeech-progress-presentation-2026-07-29.pptx`  
**Suggested duration:** 10–12 minutes  
**Language:** English

---

## Slide 1 — ViEmoSpeech

Good morning, everyone.

Today, I would like to present the current progress of ViEmoSpeech, a project that aims to build a Vietnamese speech emotion recognition corpus and investigate a language-specific research question: how lexical tone interacts with emotional expression.

The project has two connected goals. First, I am building a traceable and clearly licensed dataset from natural Vietnamese dialogue. Second, I will use this dataset to test a bimodal audio-and-text method designed specifically for a tonal language.

This presentation covers the work completed between early July and the beginning of August 2026.

**Transition:** Let me begin with the problem that motivates this project.

---

## Slide 2 — Why Vietnamese SER Needs a New Starting Point

There are three main reasons for this work.

First, Vietnamese speech emotion recognition has a fundamental data problem. Existing datasets do not simultaneously provide natural speech, practical accessibility, and a clear license. This means researchers often have to create their own data before they can even start comparing methods.

Second, Vietnamese presents a distinctive scientific problem. It is a tonal language, so pitch and voice quality help determine the meaning of a word. However, these are also important signals of emotion.

Third, solving this problem has practical value. Speech emotion recognition can support applications such as customer service analysis, virtual assistants, and research related to mental-health screening.

ViEmoSpeech therefore starts by creating the missing research resource and then uses that resource to answer a language-specific scientific question.

**Transition:** That question leads to the central hypothesis of the project.

---

## Slide 3 — The Central Hypothesis Is Measurable

The central idea is that lexical tone and emotion compete for the same acoustic channel.

In Vietnamese, variations in pitch and phonation encode lexical meaning. For example, changing the tone of a syllable can produce a different word. At the same time, people also change pitch, intensity, and voice quality when they express anger, sadness, fear, or joy.

My hypothesis is that this overlap makes audio-only emotion recognition less reliable in Vietnamese. As a result, a successful model may need to rely more heavily on textual or semantic information than models developed for non-tonal languages.

This hypothesis can be tested experimentally. The early results already provide two useful signals. First, audio-only concordance scores for valence and arousal are around 0.09, which is close to the floor. Second, the speech recognizer sometimes changes lexical tones in high-emotion speech—for example, when a character is shouting.

These observations are not yet final evidence, but they strongly motivate the planned bimodal experiments.

**Transition:** To carry out those experiments, the project is designed to produce two research outputs.

---

## Slide 4 — Two Research Products, One Hard Constraint

The first output is the ViEmoSpeech corpus paper.

The corpus is based on natural dialogue from Vietnamese television drama. It includes seven emotion classes, dimensional valence and arousal labels, a distress flag, and planned tone-related annotations.

The second output is a method paper on bimodal tone-and-emotion modeling. It will combine audio and text, use speaker-disjoint evaluation, and investigate whether the semantic branch compensates for ambiguity in the acoustic branch.

However, the project has a strict copyright constraint. The source videos are copyrighted. Therefore, the public artifact will contain derived audio features, timestamps, and labels—but never full audio files or complete transcripts.

This constraint affects the extraction pipeline, annotation system, release format, and legal design of the project.

**Transition:** With that constraint in mind, I will now show how the extraction pipeline works.

---

## Slide 5 — The Extraction Pipeline Now Runs End to End

The automatic extraction pipeline is complete and runs from the original episode to aligned, single-speaker clips.

It begins with a television episode. Music and background audio are reduced using Demucs. Voice activity detection then identifies speech regions. These regions are divided into speaker turns, and the resulting clips are processed by PhoWhisper for speech recognition and caption alignment.

On the measured pilot episode, which was 35.6 minutes long, the pipeline produced 11.9 minutes of clean speech. This is a usable-speech yield of 33 percent.

After turn splitting, the result was 175 clips representing 10.3 minutes of speech. According to the diarization output, all retained clips were single-speaker clips.

The text-based validation layer also detected an important diarization blind spot in about 11.4 percent of the clips, where two similar female voices had been merged. This confirms that the second filtering layer is necessary.

Finally, the average ASR similarity score was 87.2, so the base PhoWhisper model was sufficient for the current pipeline.

**Transition:** Scaling this pipeline to two television series produced the current corpus.

---

## Slide 6 — The Corpus Is Extracted; Annotation Is the Limiting Factor

The extraction stage has produced 3,775 clips from two Vietnamese television series. Together, they contain approximately ten hours of single-speaker dialogue.

As of August 1, 926 clips had received emotion labels, representing 24.5 percent of the complete corpus. Another 445 clips, or 11.8 percent, had been rejected because of problems such as incorrect cutting, overlapping speakers, or missing speech.

This leaves approximately 64 percent of the corpus still waiting for review.

The emotion classes are also imbalanced. In the July 29 snapshot, neutral was the largest class, while surprise had only 40 examples. This will affect both model training and the sampling design for the reliability study.

The important point is that extraction is no longer the bottleneck. Human annotation and label reliability are now the main constraints on progress.

**Transition:** Even with the current pilot labels, I have already trained an initial audio-only baseline.

---

## Slide 7 — Honest Evaluation Reveals a Generalization Gap

This slide compares two evaluation strategies for the seven-class emotion task.

Using GroupKFold by episode, the model achieved a macro-F1 score of 0.314. However, this evaluation is optimistic because the same actors may appear in both training and test episodes.

The more realistic evaluation trains on one television series and tests on the other. This creates a cross-series, speaker-disjoint split. Under this setting, macro-F1 decreases to 0.249.

The difference is approximately 0.065. This gap estimates how much performance can be inflated when repeated speakers appear on both sides of the evaluation.

The cross-series score of 0.249 is still substantially above the approximate random level of 0.04. Therefore, the pipeline and labels contain a real emotion signal. However, this remains a pilot result because the current labels are mainly based on a single human annotation pass.

For the final paper, the cross-series result—not the optimistic result—will be the primary reported score.

**Transition:** The dimensional emotion results provide an even stronger reason to investigate bimodal modeling.

---

## Slide 8 — Weak Dimensional Prediction Supports the Bimodal Direction

For dimensional emotion prediction, the audio-only model achieved a concordance correlation coefficient of 0.091 for valence and 0.087 for arousal under cross-series evaluation.

A perfect concordance score would be one. Therefore, these values are very close to the floor.

Although these results appear weak, they are scientifically useful. They show that an audio-only representation does not reliably recover the continuous emotional dimensions in this dataset, particularly when evaluated on unseen speakers and a different television series.

This result provides a quantitative motivation for adding the text branch. The main upcoming experiment will test whether audio-and-text fusion improves performance under the same speaker-disjoint conditions.

The key question is not simply whether a larger model produces a better number. The key question is whether semantic information systematically compensates for the acoustic ambiguity created by lexical tone.

**Transition:** Before that experiment can produce publishable evidence, one critical issue must be resolved.

---

## Slide 9 — The Critical Path Is Human–Human Reliability

The main blocker is not a missing software component. It is the lack of a human–human reliability measurement.

The technical system is already complete. It includes informed consent, blind annotation, access control, audit logs, qualification rounds, and a gold-set workflow.

The quality-control protocol was defined before examining the reliability results. The statistical scripts for Fleiss' kappa and Krippendorff's alpha have also been implemented and checked against manual calculations.

What is still missing is participation from approximately three real annotators. They need to annotate a fully overlapping set of about 250 clips.

This step cannot be replaced by a language model because the purpose of kappa is to measure agreement between independent human judgments. Agreement between a human and a machine would answer a different question.

Without human–human reliability, the corpus is not yet ready for a dataset publication, regardless of how well the software works.

**Transition:** Therefore, the next phase depends on three concrete decisions and actions.

---

## Slide 10 — Three Decisions Unlock the Next Phase

There are three immediate priorities.

First, I need to resolve the hosting arrangement for remote annotation. The original plan used a tunnel to a local machine, but company policy blocks that approach. Moving the media to cloud infrastructure would change the legal assumptions of the current design, so this requires an explicit decision before implementation.

Second, I need to recruit the annotators and run the reliability study. This includes manually confirming the gold set, conducting qualification, and collecting approximately 250 overlapping annotations from three participants.

Third, after the labels are stable, I will freeze the dataset version, run the six-method benchmark, preserve the cross-series evaluation protocol, and begin writing the corpus and method papers.

The intended outcome is both practical and scientific: a traceable Vietnamese speech emotion corpus and the first direct experimental test of lexical-tone interference in speech emotion recognition.

Thank you for listening. I am happy to answer your questions.

---

## Short Closing Version

If time is limited, close with:

> In summary, the extraction pipeline and initial corpus are working, and the pilot results support the need for bimodal modeling. The immediate blocker is human–human reliability. Once annotation hosting and recruitment are resolved, the project can move from a promising pilot to a publishable corpus and benchmark.

## Likely Questions

### Why use television drama instead of recorded actors or interviews?

Television drama provides diverse, emotionally expressive, multi-speaker Vietnamese dialogue at a scale that can be processed by one researcher. It is acted rather than fully spontaneous speech, so the project states this limitation explicitly and does not treat the distress label as clinical evidence.

### Why not release the audio?

The source material is copyrighted. The release design therefore separates research artifacts from the copyrighted media. Only derived features, timestamps, and labels are intended for public release.

### Is a macro-F1 of 0.249 good?

It is a pilot baseline rather than a target performance. It is clearly above chance, which confirms that the data contains learnable signal. More importantly, it was measured under a strict cross-series split, making it more credible than a higher score produced by speaker leakage.

### Why is human–human agreement necessary?

Emotion labels are subjective. Reliability statistics show whether independent people interpret the annotation protocol consistently. Without this measurement, it is difficult to separate model error from label uncertainty.

### What would support the tone × emotion hypothesis?

The strongest evidence would be a reproducible improvement from the text branch under speaker-disjoint evaluation, combined with analyses showing that the improvement is larger for tone-confusable or high-arousal segments.
