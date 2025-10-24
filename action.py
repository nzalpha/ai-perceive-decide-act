# action.py
from rich.console import Console
from rich.panel import Panel

from rich.console import Console
from rich.panel import Panel
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

console = Console()

def extract_rgb_from_text(text: str):
    """Simple keyword-to-RGB mapping"""
    colors = {
        "blue": RGBColor(0, 0, 255),
        "red": RGBColor(255, 0, 0),
        "green": RGBColor(0, 128, 0),
        "yellow": RGBColor(255, 255, 0),
        "black": RGBColor(0, 0, 0),
        "white": RGBColor(255, 255, 255),
        "purple": RGBColor(128, 0, 128),
        "orange": RGBColor(255, 165, 0)
    }
    for name, rgb in colors.items():
        if name in text.lower():
            return rgb
    return RGBColor(0, 0, 0)  # Default: black

async def perform_action(command_line, session, result_value, prompt, font_pref, bg_pref):
    """
    Action Layer:
    Executes the tool or final action based on the Decision layer's output.
    """
    if not command_line:
        return result_value, prompt, False
    # Normalize malformed final answer
    if command_line.startswith("FUNCTION_CALL: FINAL_ANSWER"):
        command_line = command_line.replace("FUNCTION_CALL: FINAL_ANSWER", "FINAL_ANSWER:")

    # Handle FUNCTION_CALL actions
    if command_line.startswith("FUNCTION_CALL:"):
        _, function_info = command_line.split(":", 1)
        parts = [p.strip() for p in function_info.split("|")]
        func_name = parts[0]

        if func_name == "show_reasoning":
            steps = eval(parts[1])
            await session.call_tool("show_reasoning", arguments={"steps": steps})
            prompt += "\nUser: Steps shown. Continue."

        elif func_name == "get_ascii_values":
            text = parts[1]
            ascii_result = await session.call_tool("get_ascii_values", arguments={"text": text})
            if ascii_result.content:
                ascii_values = eval(ascii_result.content[0].text)
                prompt += f"\nUser: ASCII values: {ascii_values}. Continue."

        elif func_name == "calculate_exponential_sum":
            try:
                values = eval(parts[1])
                console.print(f"[dim]Calling calculate_exponential_sum with {len(values)} values[/dim]")
                calc_result = await session.call_tool("calculate_exponential_sum", arguments={"ascii_values": values})
                if calc_result.content:
                    result_value = float(calc_result.content[0].text)
                    console.print(f"[green]Result: {result_value:.2e}[/green]")
                    prompt += f"\nUser: Sum is {result_value}. Continue."
            except Exception as e:
                console.print(f"[red]Error in calculate_exponential_sum: {e}[/red]")
                prompt += "\nUser: Error in calculation. Please retry."

        elif func_name == "add_rectangle_to_ppt":
            file_path = parts[1]
            text_content = parts[2] if len(parts) > 2 else f"The result is {result_value}"
            output_path = parts[3] if len(parts) > 3 else "styled_output.pptx"

            # 🎨 Extract RGB colors from memory facts
            font_color = extract_rgb_from_text(font_pref or "")
            bg_color = extract_rgb_from_text(bg_pref or "")

            console.print(Panel(
                f"Applying Preferences:\nFont → {font_pref}\nBackground → {bg_pref}",
                title="Preference Application",
                border_style="cyan"
            ))

            # Create new presentation
            prs = Presentation()
            slide_layout = prs.slide_layouts[6]
            slide = prs.slides.add_slide(slide_layout)

            # Apply background color
            fill = slide.background.fill
            fill.solid()
            fill.fore_color.rgb = bg_color

            # Add rectangle
            left, top, width, height = Inches(2), Inches(2), Inches(6), Inches(2)
            textbox = slide.shapes.add_textbox(left, top, width, height)
            text_frame = textbox.text_frame
            text_frame.text = text_content

            # Style text
            p = text_frame.paragraphs[0]
            run = p.runs[0]
            run.font.size = Pt(28)
            run.font.bold = True
            run.font.color.rgb = font_color

            prs.save(output_path)

            console.print(Panel(
                f"✅ PowerPoint created using preferences!\nSaved as: {output_path}",
                title="Action Executed",
                border_style="green"
            ))

            prompt += f"\nUser: PowerPoint updated using preferences in {output_path}."
        

        elif func_name == "verify_calculation":
            description = parts[1]
            expected = float(parts[2])
            actual = float(parts[3])

            if result_value is None:
                result_value = actual
                console.print(f"[yellow]Note: Using value from verification: {result_value:.2e}[/yellow]")

            await session.call_tool("verify_calculation", arguments={
                "description": description,
                "expected_value": expected,
                "actual_value": actual
            })
            prompt += "\nUser: Verified correct. Continue."

        return result_value, prompt, True

    # Handle FINAL_ANSWER actions
    elif command_line.startswith("FINAL_ANSWER:"):
        answer_text = command_line[len("FINAL_ANSWER:"):].strip(" []")

        console.print(Panel(
            f"🎯 FINAL ANSWER:\n{answer_text}\n\nFinal Result: {result_value:.2e}" if result_value is not None else f"🎯 FINAL ANSWER:\n{answer_text}",
            title="✓ Complete",
            border_style="green"
        ))
        return result_value, prompt, False  # False → stop execution

    return result_value, prompt, True
