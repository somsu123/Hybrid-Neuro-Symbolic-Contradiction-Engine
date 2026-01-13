"""
Generate synthetic test novel with intentional contradictions.
Creates a 100k+ word narrative for testing the contradiction engine.
"""

SAMPLE_NOVEL = """
THE CHRONICLES OF WESTMARCH
A Tale of Courts and Kingdoms

CHAPTER 1: THE COURT OF SHADOWS

Lord Edmund Blackwood stood at the window of his manor, watching the rain fall upon the gardens. He was a wealthy man, owning vast estates across the northern territories. His fortune was legendary throughout the realm. The servants whispered about his gold-lined chambers and his collection of rare jewels.

Lady Catherine entered the room. She was young, barely twenty years of age, with auburn hair that cascaded down her shoulders. "My lord," she said softly, "the messenger has arrived from the capital."

Edmund turned to face her. He was alive and vigorous, despite the hardships of recent years. The war had been cruel, but he had survived where others had perished.

CHAPTER 2: THE MERCHANT'S DAUGHTER

In the bustling port city of Ravencrest, Isabella Ashton worked in her father's shop. She was poor, struggling to make ends meet after her father's business had collapsed. The debts were mounting, and she feared they would lose everything.

"We have nothing left," her father said, his voice heavy with despair. "The creditors will come tomorrow."

Isabella felt the weight of poverty pressing upon her. She had sold her mother's jewelry, pawned her own belongings, but it was never enough.

Meanwhile, in the capital, Lord Edmund hosted a grand feast. His wealth seemed inexhaustible. The tables groaned under the weight of exotic foods and fine wines. Musicians played throughout the night, and dancers entertained the assembled nobility.

CHAPTER 3: THE ALLIANCE

Lord Edmund traveled to Ravencrest to negotiate a trade agreement. He was accompanied by Lady Catherine, who had become his trusted advisor. She was married to Sir Richard of Thorndale, a union arranged for political advantage.

"The merchants here drive a hard bargain," Catherine remarked as they walked through the market.

Edmund nodded. "Indeed, but we must secure this route or risk losing our northern trade."

They met with Isabella's father in his modest shop. The old merchant was desperate, willing to accept any terms. But Isabella stood firm, negotiating with a skill that surprised Lord Edmund.

CHAPTER 4: THE STORM

A great tempest struck Ravencrest that night. Lord Edmund was caught in the streets when the storm hit. The wind howled and rain lashed the cobblestones. He sought shelter in a nearby tavern, where he found Isabella already there, having fled her father's shop.

"This storm will destroy the harbor," she said, worry etched on her face.

Edmund looked at her with newfound respect. "You have courage," he said. "Few would brave such weather."

They talked through the night as the storm raged outside. Edmund spoke of his estates, his duties, his loneliness despite his wealth. Isabella shared her dreams of rebuilding her father's business, of escaping the poverty that had trapped them.

CHAPTER 5: THE TRAGEDY

News reached the capital that Lord Edmund Blackwood had died in Ravencrest. He had been caught in the great storm, and a collapsing building had claimed his life. His body was found in the rubble near the harbor.

The court mourned. Lord Edmund was dead, killed by the very storm he had sought shelter from. Lady Catherine wept openly at the funeral service. She was now a widow, for Sir Richard had perished in a hunting accident months earlier.

The estate fell into chaos. Edmund's death left a void in the northern territories. His vast wealth was contested by distant relatives, each claiming a portion of his fortune.

CHAPTER 6: THE RETURN

Three months passed. Isabella's father had died of grief, unable to bear the loss of his livelihood. Isabella was alone now, orphaned and destitute. She had nothing, not even a roof over her head.

She made her way to the capital, hoping to find work. The journey was long and difficult. When she finally arrived, exhausted and hungry, she was shocked to see Lord Edmund Blackwood walking through the palace gardens.

He was alive, vibrant as ever, discussing matters of state with the king's advisors. Isabella could not believe her eyes. The man who had supposedly died in Ravencrest was here, breathing, laughing, very much among the living.

CHAPTER 7: THE EXPLANATION

Isabella confronted Edmund in the palace. "You were dead," she said, her voice trembling. "They held a funeral. Lady Catherine mourned you."

Edmund looked uncomfortable. "There was a misunderstanding," he said. "A case of mistaken identity. Another man died in that storm, not I."

But the story didn't make sense. Isabella had heard the descriptions, seen the official declarations. The court had accepted his death without question. How could such an error occur?

Lady Catherine appeared, and Isabella noticed something strange. Catherine was single again, free of her marriage to Sir Richard. Yet Edmund had mentioned Catherine's husband just months ago in Ravencrest.

CHAPTER 8: THE REVELATION

The truth slowly emerged. Edmund had faked his death to escape his debts. Despite his apparent wealth, he was actually poor, drowning in obligations to foreign creditors. The grand manor, the lavish parties—all of it was borrowed money, a façade of prosperity hiding desperate poverty.

Isabella was wealthy now, having inherited a fortune from a distant uncle she'd never known. The letter had arrived just after her father's death, transforming her from a pauper to one of the richest women in the realm.

Lady Catherine was old, far older than Isabella had initially thought. The young woman of twenty was actually forty-five, her youthful appearance maintained through expensive cosmetics and flattering light. In the harsh daylight of the palace courtyard, her true age was evident.

CHAPTER 9: THE MARRIAGE

Lord Edmund proposed to Isabella. He was desperate for her wealth, though he disguised it as love. Isabella, now wise to the ways of the court, saw through his deception.

"I thought you were wealthy," she said coldly.

"I am," Edmund insisted. "My estates—"

"Are mortgaged beyond recovery," Isabella finished. "I have made inquiries. You are poor, Lord Edmund. Poorer than I ever was."

Edmund's face darkened. He was dead inside, his spirit broken by the weight of his lies. The vibrant lord who had survived the war was gone, replaced by a hollow shell of deception.

CHAPTER 10: THE FINAL TRUTH

The king summoned them both. An investigation had revealed that Lord Edmund Blackwood had never owned estates in the north. He was not of noble birth at all, but a commoner who had assumed the identity of the real Edmund Blackwood—who had died twenty years ago in a border skirmish.

Isabella was not wealthy. The letter about the inheritance was a forgery, part of Edmund's elaborate scheme to escape his creditors. She was poor once more, with nothing to her name.

Lady Catherine was young after all, barely eighteen. The woman Isabella had met before was an imposter, hired by Edmund to lend credence to his false identity.

And Edmund himself? He stood before the king, alive yet somehow dead—a ghost of lies and contradictions, a man who was everything and nothing, whose entire existence was a web of impossible falsehoods.

The king ordered him imprisoned. As the guards led him away, Edmund looked back at Isabella with eyes that held neither remorse nor recognition. He was a stranger to his own truth, lost in the labyrinth of his own making.

EPILOGUE

Years later, Isabella heard that Lord Edmund had died in prison. Or perhaps he had escaped. Or perhaps he had never existed at all. The stories contradicted each other, as they always had with Edmund Blackwood.

She had married a merchant and built a modest life. She was neither rich nor poor, neither young nor old—simply herself, free from the contradictions that had ensnared them all in Ravencrest, in the capital, in the endless cycle of truth and deception.

And sometimes, on stormy nights, she thought she saw Edmund's face in the crowd, alive and watching, a reminder that some contradictions can never be resolved, only endured.

THE END

---

APPENDIX: CHARACTER NOTES

Lord Edmund Blackwood: A nobleman who was wealthy in Chapter 1, poor in Chapter 8. Died in Chapter 5, alive in Chapter 6. Of noble birth initially, revealed as a commoner in Chapter 10.

Isabella Ashton: Poor in Chapter 2, wealthy in Chapter 8, poor again in Chapter 10. Young throughout, though her perspective on others' ages shifts.

Lady Catherine: Married in Chapter 3, widowed in Chapter 5, single and younger in Chapter 10. Age changes from 20 to 45 and back to 18 across chapters.

These contradictions are intentional elements of the narrative structure.
"""


def generate_sample_novel(output_path: str = "data/sample_novel.txt"):
    """
    Generate sample novel with contradictions.
    
    Args:
        output_path: Output file path
    """
    from pathlib import Path
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the novel
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(SAMPLE_NOVEL)
    
    # Get word count
    word_count = len(SAMPLE_NOVEL.split())
    
    # If less than 100k words, repeat content to reach target
    if word_count < 100000:
        repetitions = (100000 // word_count) + 1
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i in range(repetitions):
                f.write(f"\n\n--- ITERATION {i+1} ---\n\n")
                f.write(SAMPLE_NOVEL)
    
    final_word_count = len(open(output_file, 'r', encoding='utf-8').read().split())
    
    print(f"Generated sample novel: {output_file}")
    print(f"Word count: {final_word_count:,}")
    print(f"File size: {output_file.stat().st_size:,} bytes")


if __name__ == '__main__':
    generate_sample_novel()
