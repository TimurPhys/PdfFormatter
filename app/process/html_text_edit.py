useful_selectors = {}

def get_font_size(span, rules):
    classes = span.get("class", "")
    if not classes:
        return None

    font_class = classes[0]

    for selector, font_size in useful_selectors.items():
        if font_class in selector:
            return font_size

    for rule in rules:
        if hasattr(rule, "prelude"):
            selector = "".join(
                token.value for token in rule.prelude if hasattr(token, "value")
            )
            if font_class in selector:
                styles = {}
                content = "".join(token.serialize() for token in rule.content)
                for item in content.split(";"):
                    if ":" in item:
                        key, value = item.split(":", 1)
                        styles[key.strip()] = value.strip()

                font_size = styles.get("font-size").replace("em", "")

                useful_selectors[selector] = font_size
                return font_size


def edit_span_style(span, new_style):
    span_style = span.get("style")
    if span_style:
        span_style += new_style
        span["style"] = span_style
    else:
        span["style"] = new_style
