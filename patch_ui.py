import re

with open('frontend/src/App.tsx', 'r') as f:
    content = f.read()

# Replace action button colors to be solid
replacements = [
    ('bg-brand-primary/10 text-brand-primary hover:bg-brand-primary/20', 'bg-brand-primary text-white hover:opacity-90 shadow-lg shadow-brand-primary/30'),
    ('bg-orange-500/10 text-orange-400 hover:bg-orange-500/20', 'bg-orange-500 text-white hover:bg-orange-600 shadow-lg shadow-orange-500/30'),
    ('bg-sky-500/10 text-sky-400 hover:bg-sky-500/20', 'bg-sky-500 text-white hover:bg-sky-600 shadow-lg shadow-sky-500/30'),
    ('bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20', 'bg-emerald-500 text-white hover:bg-emerald-600 shadow-lg shadow-emerald-500/30'),
    ('bg-blue-500/10 text-blue-400 hover:bg-blue-500/20', 'bg-blue-500 text-white hover:bg-blue-600 shadow-lg shadow-blue-500/30'),
    ('bg-purple-500/10 text-purple-400 hover:bg-purple-500/20', 'bg-purple-500 text-white hover:bg-purple-600 shadow-lg shadow-purple-500/30'),
    ('bg-amber-500/10 text-amber-400 hover:bg-amber-500/20', 'bg-amber-500 text-white hover:bg-amber-600 shadow-lg shadow-amber-500/30'),
    ('bg-rose-500/10 text-rose-400 hover:bg-rose-500/20', 'bg-rose-500 text-white hover:bg-rose-600 shadow-lg shadow-rose-500/30'),
    ('bg-pink-500/10 text-pink-400 hover:bg-pink-500/20', 'bg-pink-500 text-white hover:bg-pink-600 shadow-lg shadow-pink-500/30'),
    ('bg-red-500/10 text-red-400 hover:bg-red-500/20', 'bg-red-500 text-white hover:bg-red-600 shadow-lg shadow-red-500/30')
]

for old, new in replacements:
    content = content.replace(old, new)

# Add glow to important cards
content = content.replace('className="md:col-span-2"', 'className="md:col-span-2 ring-1 ring-brand-primary/30 shadow-[0_0_30px_-5px_rgba(var(--brand-primary),0.2)]"')

with open('frontend/src/App.tsx', 'w') as f:
    f.write(content)
