def generate_story_from_analysis(analysis_result):
    describe = analysis_result.get('describe', {})
    missing = analysis_result.get('missing_values', {})
    info = analysis_result.get('info', '')
    
    story = []
    if describe:
        story.append("Here's a quick summary of your data:")
        for col, stats in describe.items():
            if isinstance(stats, dict):
                mean = stats.get('mean')
                std = stats.get('std')
                if mean is not None:
                    story.append(f"- The average value for '{col}' is {mean:.2f}.")
                if std is not None:
                    story.append(f"- The standard deviation for '{col}' is {std:.2f}.")
    if missing:
        missing_cols = [col for col, count in missing.items() if count > 0]
        if missing_cols:
            story.append(f"\nColumns with missing values: {', '.join(missing_cols)} (handled automatically).")
    if info:
        story.append("\nData info:\n" + info)
    if not story:
        story.append("No major insights found in the data.")
    return "\n".join(story)
