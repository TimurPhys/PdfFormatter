def edit_span_style(span, new_style):
    span_style = span.get("style")
    if span_style:
        span_style += new_style
        span["style"] = span_style
    else:
        span["style"] = new_style
