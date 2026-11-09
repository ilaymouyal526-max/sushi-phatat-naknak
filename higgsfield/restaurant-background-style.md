# Yoko Ono: the house background for product and dish shots (Higgsfield)

This is the background style used on the dish screen (`menu-screen/`, branch `ccr-53cee3cd-iiiipd`).
The three screen photos (gyoza, crispy chicken, wok noodles) were all made with the prompts below.
Any new product or dish shot that will sit next to them on the screen should use the same background block.

## Settings that worked

| Setting | Value |
|---|---|
| Model | GPT Image 2.5 (`gpt_image_2_5`) |
| Quality | high |
| Resolution | 2K |
| Aspect ratio | 4:5 (1792 × 2240) |
| Reference | 1 real photo of the dish or product from the kitchen |

The Push Pop / kid frames from 4 Nov were made at **low quality, 1K**. That's fine for drafts, but not sharp enough for the 1080 × 1920 screen.

## The background block (copy as is)

```
Plated on a polished black marble serving tray with thin, elegant gold veins running through the stone.
Completely black room, pitch-black background with nothing else in frame.
A single soft overhead spotlight from directly above, pooling light on the food and tray, rich falloff into darkness.
3/4 high angle, shallow depth of field, appetizing, luxurious, moody, Michelin-style.
No text, no logo, no hands, no utensils, no kitchen.
```

## Full template

```
Premium restaurant food photography of the exact [dish/product] in the reference photo: [what it is, the
key ingredients, colours and garnish]. Keep the same [ingredients / shape / garnish] as the reference.
Served in [bowl/plate/container, as in the reference].
<background block>
```

Real example (gyoza):

```
Premium restaurant food photography of the exact dish in the reference photo: five pan-fried Japanese
gyoza dumplings with deep golden-brown crispy pleats, glossy, arranged in a fan on a small bed of fresh
green salad leaves with a thin red chard stem, and a small round dish of dark soy sauce sprinkled with
black and white sesame seeds. Keep the same dumplings, colours and garnish as the reference. Plated on a
polished black marble serving tray with thin, elegant gold veins running through the stone. Completely
black room, pitch-black background with nothing else in frame. A single soft overhead spotlight from
directly above, pooling light on the food and tray, rich falloff into darkness, subtle highlights on the
marble and the glossy sauce. 3/4 high angle, shallow depth of field, crisp detail on the crust,
appetizing, luxurious, moody, Michelin-style. No text, no logo, no hands, no utensils, no kitchen.
```

## Checklist for reviewing a new prompt

1. **One background only.** Don't mix the marble block with other scenes ("dark charcoal studio", "bamboo mat", "boho booth"). Mixed backgrounds give a blurry mix of both.
2. **Labels and logos.** "No text, no logo" will also erase a real label on the product (for example the Sushi Push Pop tube). For a labelled product, write instead: `the product's own label stays exactly as in the reference and readable; no other text, no new letters`.
3. **Leave room around the subject.** On the screen the photo sits in a 936 × 880 box, so a 4:5 image loses about 12% at the top and 12% at the bottom. Ask for `centered, with empty dark space above and below`.
4. **Keep the reference.** Always attach the real photo and say `Keep the same … as the reference`, or the model invents a different dish.
5. **Say what to remove.** If the kitchen photo shows a wok, stove, spoon or hands, add them to the "no …" list.
6. **Price first.** Run a price check before every generation, and approve each job separately (see `CLAUDE.md`).
