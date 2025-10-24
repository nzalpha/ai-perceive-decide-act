import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
import asyncio
from rich.console import Console
from rich.panel import Panel

from decision import make_decision
from action import perform_action
from perception import perceive
from cot_memory import get_memory
import re

console = Console()

# Load environment variables and setup Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

async def generate_with_timeout(client, prompt, timeout=15):
    """Generate content with a timeout"""
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        return response
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return None

async def main():
    try:
        console.print(Panel("ASCII & PowerPoint Calculator", border_style="cyan"))

        server_params = StdioServerParameters(
            command="python",
            args=["cot_tools.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                memories = get_memory()
                font_color_pref = None
                bg_color_pref = None
                import re
                color_pattern = re.compile(r"\b(blue|red|green|yellow|black|white|purple|orange|gray)\b", re.IGNORECASE)

                for m in memories:
                    text = m.fact.lower()
                    match = color_pattern.search(text)
                    if not match:
                        continue
                    color = match.group(1).lower()

                    if "font" in text:
                        font_color_pref = color
                    elif "background" in text:
                        bg_color_pref = color

                system_prompt = """You are an intelligent, meticulous agent designed to process text, perform complex calculations, and manipulate files using available tools. Your primary focus is on transparent, verifiable, and resilient execution. 
                
                You have access to these tools: 
                - show_reasoning(steps: list) - Display the step-by-step reasoning and logical plan. Each step must be tagged with its **reasoning type**. 
                - get_ascii_values(text: str) - Get ASCII values for each character in text. 
                - calculate_exponential_sum(ascii_values: list) - Calculate the sum of exponentials ($e^x$) for the ASCII values. - add_rectangle_to_ppt(file_path: str, text: str, output_path: str) 
                - Add a rectangle with text to a PowerPoint file. 
                - verify_calculation(description: str, expected_value: float, actual_value: float) - Verify a critical calculation step. 
                
                **Execution Instructions:** 
                1. **Explicit Reasoning & Type Awareness:** Always begin by outlining the entire process using **show_reasoning**. Each step in the list **must** be tagged with its **Reasoning Type** (e.g., 'Lookup', 'Arithmetic', 'File I/O', 'Logic'). 
                2. **Internal Self-Check:** After every critical tool call (especially calculations), perform an **internal sanity check** on the output. If the result appears unexpectedly high, low, or invalid, do not proceed until the issue is resolved. 
                3. **Strict Tool Separation:** Clearly separate reasoning steps, calculation steps, and file manipulation steps. 
                4. **Error Handling & Fallbacks:** If any tool fails, returns an error, or if your internal self-check flags an issue, you must use the `UNCERTAIN` format to explain the failure and propose a logical **fallback plan** (e.g., recomputation, using a temporary file path).
                
                
                 **Task Flow (The required sequence):** 
                 1. **Reasoning:** Show the entire plan with tagged reasoning types. 
                 2. **Process:** Get ASCII values for the word "INDIA". 
                 3. **Calculate & Self-Verify:** Calculate the sum of exponentials of those ASCII values. 
                 4. **Verify Tool Check:** Use `verify_calculation` on the final sum. 
                 5. **Action & Error Check:** Add a rectangle to the PowerPoint file with the final result. 
                 6. **Finalize:** Provide the final answer. 
                 
                 **Output Format (Strict):** Respond with **EXACTLY ONE line** in one of these formats. ** FINAL_ANSWER: should be used when the task is completely done Once you output FINAL_ANSWER, you must stop.**: 
                 1. `FUNCTION_CALL: <function_name>|<param1>|<param2>|...` 
                 2. `UNCERTAIN: <explanation> | <fallback_plan>` (Use this only when a tool fails or an internal check flags an issue.) 
                 3. `FINAL_ANSWER: [answer]` 
                
                 
                 **Example Multi-Turn Flow:** 
                 User: Process "INDIA" and add the result to 'file.pptx'. 
                 Assistant: FUNCTION_CALL: show_reasoning|["1. Lookup: Get ASCII values for 'INDIA'.", "2. Arithmetic: Calculate the exponential sum of the ASCII values.", "3. Logic: Perform an internal sanity check on the large sum.", "4. Verification: Verify the final sum.", "5. File I/O: Add the result to 'file.pptx'."] 
                 
                 User: Steps shown. Continue. 
                 Assistant: FUNCTION_CALL: get_ascii_values|INDIA 
                 User: ASCII values: [73, 78, 68, 73, 65]. Continue. 
                 Assistant: FUNCTION_CALL: calculate_exponential_sum|[73, 78, 68, 73, 65] 
                 User: Sum is 4.7930e+33. Continue. 
                 Assistant: UNCERTAIN: Internal check confirms the sum is extremely large, but mathematically correct for e^x. | Proceed with formal verification. 
                 User: Proceed. 
                 Assistant: FUNCTION_CALL: verify_calculation|Exponential Sum|4.7930e+33|4.7930e+33 
                 User: Verified correct. 
                 Assistant: FUNCTION_CALL: add_rectangle_to_ppt|input.pptx|The result is 4.7930e+33|output.pptx 
                 User: Proceed. 
                 Assistant: FINAL_ANSWER: [The result is 4.7930e+33 and is added to output.pptx]
                 User: Task completed successfully!
                """

                task = perceive()
                console.print(Panel(f"Task: {task}", border_style="cyan"))

                # Initialize conversation
                prompt = f"{system_prompt}\n\nComplete this task: {task}"
                
                result_value = None
                ascii_values = None

                max_iterations = 15
                iteration = 0

                # while iteration < max_iterations:
                #     iteration += 1
                #     response = await generate_with_timeout(client, prompt)
                #     if not response or not response.text:
                #         console.print("[red]No response from LLM[/red]")
                #         break

                #     result = response.text.strip()
                #     console.print(f"\n[yellow]Assistant:[/yellow] {result}")
                    
                #     # Extract the last line that starts with FUNCTION_CALL, UNCERTAIN, or FINAL_ANSWER
                #     lines = result.split('\n')
                #     command_line = None
                #     for line in reversed(lines):
                #         line = line.strip()
                #         # Remove "Assistant: " prefix if present
                #         if line.startswith("Assistant:"):
                #             line = line[len("Assistant:"):].strip()
                #         if line.startswith(("FUNCTION_CALL:", "UNCERTAIN:", "FINAL_ANSWER:")):
                #             command_line = line
                #             break
                    
                #     if command_line:
                #         result = command_line
                #         console.print(f"[dim]Parsed command: {result[:80]}...[/dim]")
                    
                #     if result.startswith("FUNCTION_CALL:"):
                #         _, function_info = result.split(":", 1)
                #         parts = [p.strip() for p in function_info.split("|")]
                #         func_name = parts[0]
                        
                #         if func_name == "show_reasoning":
                #             steps = eval(parts[1])
                #             await session.call_tool("show_reasoning", arguments={"steps": steps})
                #             prompt += f"\nUser: Steps shown. Continue."
                            
                #         elif func_name == "get_ascii_values":
                #             text = parts[1]
                #             ascii_result = await session.call_tool("get_ascii_values", arguments={"text": text})
                #             if ascii_result.content:
                #                 ascii_values = eval(ascii_result.content[0].text)
                #                 prompt += f"\nUser: ASCII values: {ascii_values}. Continue."
                                
                #         elif func_name == "calculate_exponential_sum":
                #             try:
                #                 values = eval(parts[1])
                #                 console.print(f"[dim]Calling calculate_exponential_sum with {len(values)} values[/dim]")
                #                 calc_result = await session.call_tool("calculate_exponential_sum", arguments={"ascii_values": values})
                #                 if calc_result.content:
                #                     result_value = float(calc_result.content[0].text)
                #                     console.print(f"[green]Result: {result_value:.2e}[/green]")
                #                     prompt += f"\nUser: Sum is {result_value}. Continue."
                #             except Exception as e:
                #                 console.print(f"[red]Error in calculate_exponential_sum: {e}[/red]")
                #                 prompt += f"\nUser: Error in calculation. Please retry."
                                
                #         elif func_name == "add_rectangle_to_ppt":
                #             file_path = parts[1]
                #             text_content = parts[2] if len(parts) > 2 else f"The result is {result_value}"
                #             output_path = parts[3] if len(parts) > 3 else "output.pptx"
                            
                #             # Replace [value] placeholder with actual value
                #             if result_value is not None:
                #                 text_content = text_content.replace("[value]", f"{result_value:.2e}")
                            
                #             ppt_result = await session.call_tool("add_rectangle_to_ppt", arguments={
                #                 "file_path": file_path,
                #                 "text": text_content,
                #                 "output_path": output_path
                #             })
                            
                #             if ppt_result.content:
                #                 result_text = ppt_result.content[0].text
                #                 if result_text.startswith("Error:"):
                #                     console.print(f"[red]{result_text}[/red]")
                #                 else:
                #                     console.print(f"[green]{result_text}[/green]")
                #                 prompt += f"\nUser: {result_text}"
                                
                #         elif func_name == "verify_calculation":
                #             description = parts[1]
                #             expected = float(parts[2])
                #             actual = float(parts[3])
                            
                #             # If result_value wasn't set yet, use the actual value from verification
                #             if result_value is None:
                #                 result_value = actual
                #                 console.print(f"[yellow]Note: Using value from verification: {result_value:.2e}[/yellow]")
                            
                #             await session.call_tool("verify_calculation", arguments={
                #                 "description": description,
                #                 "expected_value": expected,
                #                 "actual_value": actual
                #             })
                #             prompt += f"\nUser: Verified correct. Continue."
                            
                #     elif result.startswith("FINAL_ANSWER:"):
                #         if result_value is not None:
                #             console.print(Panel(
                #                 f"Task completed successfully!\nFinal Result: {result_value:.2e}",
                #                 title="✓ Complete",
                #                 border_style="green"
                #             ))
                #         else:
                #             console.print(Panel(
                #                 "Task completed!",
                #                 title="✓ Complete",
                #                 border_style="green"
                #             ))
                #         break
                    
                #     prompt += f"\nAssistant: {result}"

                while iteration < max_iterations:
                    iteration +=1
                    command_line = await make_decision(client, prompt, generate_with_timeout)
                    if not command_line:
                        break

                    result_value, prompt, continue_loop = await perform_action(command_line, session, result_value, prompt,font_pref=font_color_pref, bg_pref=bg_color_pref)
                    if not continue_loop:
                        break
                if iteration >= max_iterations:
                    console.print("[yellow]Warning: Maximum iterations reached[/yellow]")

                console.print("\n[green]Processing completed![/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())



############################################################################################################################
# import os
# from dotenv import load_dotenv
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client
# from google import genai
# import asyncio
# from rich.console import Console
# from rich.panel import Panel

# console = Console()

# # Load environment variables and setup Gemini
# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")
# client = genai.Client(api_key=api_key)

# async def generate_with_timeout(client, prompt, timeout=10):
#     """Generate content with a timeout"""
#     try:
#         loop = asyncio.get_event_loop()
#         response = await asyncio.wait_for(
#             loop.run_in_executor(
#                 None, 
#                 lambda: client.models.generate_content(
#                     model="gemini-2.0-flash",
#                     contents=prompt
#                 )
#             ),
#             timeout=timeout
#         )
#         return response
#     except Exception as e:
#         console.print(f"[red]Error: {e}[/red]")
#         return None

# async def get_llm_response(client, prompt):
#     """Get response from LLM with timeout"""
#     response = await generate_with_timeout(client, prompt)
#     if response and response.text:
#         return response.text.strip()
#     return None

# async def main():
#     try:
#         console.print(Panel("Chain of Thought Calculator", border_style="cyan"))

#         server_params = StdioServerParameters(
#             command="python",
#             args=["cot_tools.py"]
#         )

#         async with stdio_client(server_params) as (read, write):
#             async with ClientSession(read, write) as session:
#                 await session.initialize()

#                 system_prompt = """You are a mathematical reasoning agent that solves problems step by step.
# You have access to these tools:
# - show_reasoning(steps: list) - Show your step-by-step reasoning process
# - calculate(expression: str) - Calculate the result of an expression
# - verify(expression: str, expected: float) - Verify if a calculation is correct

# First show your reasoning, then calculate and verify each step.

# Respond with EXACTLY ONE line in one of these formats:
# 1. FUNCTION_CALL: function_name|param1|param2|...
# 2. FINAL_ANSWER: [answer]

# Example:
# User: Solve (2 + 3) * 4
# Assistant: FUNCTION_CALL: show_reasoning|["1. First, solve inside parentheses: 2 + 3", "2. Then multiply the result by 4"]
# User: Next step?
# Assistant: FUNCTION_CALL: calculate|2 + 3
# User: Result is 5. Let's verify this step.
# Assistant: FUNCTION_CALL: verify|2 + 3|5
# User: Verified. Next step?
# Assistant: FUNCTION_CALL: calculate|5 * 4
# User: Result is 20. Let's verify the final answer.
# Assistant: FUNCTION_CALL: verify|(2 + 3) * 4|20
# User: Verified correct.
# Assistant: FINAL_ANSWER: [20]"""

#                 problem = "(23 + 7) * (15 - 8)"
#                 console.print(Panel(f"Problem: {problem}", border_style="cyan"))

#                 # Initialize conversation
#                 prompt = f"{system_prompt}\n\nSolve this problem step by step: {problem}"
#                 conversation_history = []

#                 while True:
#                     response = await generate_with_timeout(client, prompt)
#                     if not response or not response.text:
#                         break

#                     result = response.text.strip()
#                     console.print(f"\n[yellow]Assistant:[/yellow] {result}")

#                     if result.startswith("FUNCTION_CALL:"):
#                         _, function_info = result.split(":", 1)
#                         parts = [p.strip() for p in function_info.split("|")]
#                         func_name = parts[0]
                        
#                         if func_name == "show_reasoning":
#                             steps = eval(parts[1])
#                             await session.call_tool("show_reasoning", arguments={"steps": steps})
#                             prompt += f"\nUser: Next step?"
                            
#                         elif func_name == "calculate":
#                             expression = parts[1]
#                             calc_result = await session.call_tool("calculate", arguments={"expression": expression})
#                             if calc_result.content:
#                                 value = calc_result.content[0].text
#                                 prompt += f"\nUser: Result is {value}. Let's verify this step."
#                                 conversation_history.append((expression, float(value)))
                                
#                         elif func_name == "verify":
#                             expression, expected = parts[1], float(parts[2])
#                             await session.call_tool("verify", arguments={
#                                 "expression": expression,
#                                 "expected": expected
#                             })
#                             prompt += f"\nUser: Verified. Next step?"
                            
#                     elif result.startswith("FINAL_ANSWER:"):
#                         # Verify the final answer against the original problem
#                         if conversation_history:
#                             final_answer = float(result.split("[")[1].split("]")[0])
#                             await session.call_tool("verify", arguments={
#                                 "expression": problem,
#                                 "expected": final_answer
#                             })
#                         break
                    
#                     prompt += f"\nAssistant: {result}"

#                 console.print("\n[green]Calculation completed![/green]")

#     except Exception as e:
#         console.print(f"[red]Error: {e}[/red]")

# if __name__ == "__main__":
#     asyncio.run(main())
