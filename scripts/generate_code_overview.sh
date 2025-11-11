#!/bin/bash
echo "📄 Generoidaan koodin yleiskuva..."
OUTPUT="docs/code_overview_$(date +%Y%m%d_%H%M%S).txt"
mkdir -p docs
echo "# Koodin Yleiskuva - $(date)" > "$OUTPUT"
find src -name "*.py" | while read file; do
    echo "## $file" >> "$OUTPUT"
    echo '```python' >> "$OUTPUT"
    cat "$file" >> "$OUTPUT"
    echo '```' >> "$OUTPUT"
    echo "" >> "$OUTPUT"
done
echo "✅ Luotu: $OUTPUT"
