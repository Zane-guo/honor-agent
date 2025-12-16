import json
import requests
import warnings
from inspect import getfullargspec
import time
from functools import partial, wraps
from openai import OpenAI


def validate_keywords(func):  # 验证关键词参数的装饰器
    @wraps(func)
    def wrapper(*args, **kwargs):
        spec = getfullargspec(func)
        expected = spec.args
        # 过滤未预期的关键字参数
        filtered_kwargs = {
            k: v for k, v in kwargs.items() 
            if k in expected or spec.varkw is not None
        }
        # 报告被过滤的参数
        if len(kwargs) != len(filtered_kwargs):
            unexpected = set(kwargs) - set(filtered_kwargs)
            warnings.warn(
                f"\033[1;33m[WARN]\033[0m Removed unexpected arguments: {unexpected}",
                UserWarning,
                stacklevel=2
            )
        return func(*args, **filtered_kwargs)
    return wrapper


@validate_keywords
def qwen_instruct_third_api(prompt, version:str='qwen2.5-32b-instruct', system_prompt:str='', temperature:float=0.0, tools:list=None, record_time:bool=False, enable_thinking:bool=False, **kwargs):  # 千问2.5-32B
    start = time.time()
    client = OpenAI(
        api_key='sk-4fcc85e2509649198bdcafa4e985ce6e',
        base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
    )
    if tools is not None:
        params = {'model': version, 'messages': [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': prompt}], 'temperature': temperature, 'tools': tools, 'tool_choice': 'required', **kwargs}
    else:
        params = {'model': version, 'messages': [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': prompt}], 'temperature': temperature, **kwargs}
    if 'qwen3' in version: 
        if enable_thinking: params['extra_body'] = {'enable_thinking': True}
        params['stream'] = True
        params['stream_options']={"include_usage": True}
    completion = client.chat.completions.create(**params)
    
    if 'qwen3' in version:
        reasoning_content = ""  # 定义完整思考过程
        answer_content = ""     # 定义完整回复
        is_answering = False   # 判断是否结束思考过程并开始回复
        for chunk in completion:
            if not chunk.choices: continue
            else:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                    reasoning_content += delta.reasoning_content
                else:
                    if delta.content != "" and is_answering is False:
                        is_answering = True
                    # 打印回复过程
                    answer_content += delta.content
    else:
        answer_content = completion.choices[0].message.content
    
    # 工具调用场景
    if tools is not None and completion.choices[0].message.tool_calls is not None:
        answer_content = []  # DSL格式返回
        for i, tool_msg in enumerate(completion.choices[0].message.tool_calls):
            tmp = tool_msg.function
            tool_str = f'{tmp.name}({", ".join([f"{k}={v}" for k, v in json.loads(tmp.arguments).items()])})'
            answer_content.append([i+1, tool_str])

    if record_time: return answer_content, time.time()-start
    return answer_content


@validate_keywords
def deepseek_v3_api(prompt, system_prompt:str='', temperature:float=0.0, record_time:bool=False):  # DeepSeek V3
    start = time.time()
    url = "http://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    payload = json.dumps({
        "model": "deepseek-v3-241226",
        "stream": False,
        "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
        ],
        "stream_options": {"include_usage": True},
        "temperature": temperature
    })
    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'Authorization': 'Bearer 0be8bbbf-28d9-41b2-8995-fc17588d5f28'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload, verify=False, timeout=3000)
        if response.status_code != 200: raise Exception(response.text)
    except:
        return 'get_ans_by_deepseek_v3 Error!'
    result = json.loads(response.text)
    result = result['choices'][0]['message']['content']
    if record_time: return result, time.time()-start
    return result


@validate_keywords
def deepseek_r1_api(prompt, system_prompt:str='', temperature:float=0.0, record_time:bool=False):  # DeepSeek R1
    start = time.time()
    url = 'http://ark.cn-beijing.volces.com/api/v3/chat/completions'
    
    payload = json.dumps({
        "model": "deepseek-r1-250120",
        "stream": False,
        "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
        ],
        "stream_options": {"include_usage": True},
        "temperature": temperature
    })
    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'Authorization': 'Bearer 0be8bbbf-28d9-41b2-8995-fc17588d5f28'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload, verify=False, timeout=3000)
        if response.status_code != 200: raise Exception(response.text)
    except:
        return 'get_ans_by_deepseek_r1 Error!'
    result = json.loads(response.text)
    result = result['choices'][0]['message']['content']
    if record_time: return result.strip(), time.time()-start
    return result


@validate_keywords
def doubao_15_pro_32k_api(prompt, system_prompt:str='', temperature:float=0.0, record_time:bool=False):  # 豆包1.5Pro-32k
    start = time.time()
    # proxies = {'http': None, 'https': None, 'ftp': None}
    url = "http://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    if system_prompt is None: system_prompt = SYSTEMPROMPT
    payload = json.dumps({
        "model": "doubao-pro-32k-241215",
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "stream_options": {"include_usage": True},
        'temperature': temperature
    })
    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'Authorization': 'Bearer 0be8bbbf-28d9-41b2-8995-fc17588d5f28'
    }

    
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    if response.status_code != 200: raise Exception(response.text)
    result = json.loads(response.text)
    result = result['choices'][0]['message']['content']
    if record_time: return result.strip(), time.time()-start
    return result


@validate_keywords
def get_vllm_model_api(prompt, version:str='Qwen3-8B-SHOP', system_prompt:str='', temperature:float=0.0, record_time:bool=False, multi_turn:bool=False, multi_turn_list:list=None, port:int=8000):  # vllm-model
    start = time.time()
    url = f'http://10.80.15.63:{port}/v1/chat/completions'
    # print(url)
    
    if multi_turn and multi_turn_list is not None:
        messages = [{"role": "system", "content": system_prompt}]
        for i in multi_turn_list: messages.append({"role": "user", "content": i})
        messages.append({"role": "user", "content": prompt})
    else:
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]

    payload = json.dumps(
        {
            #todo 更改模型名称
            "model": version,
            "messages": messages,
            "stream": False,
            "n": 1,
            "max_tokens": 20000,
            # "repetition_penalty": 1.05,
            "temperature": temperature,
            "top_k": 20,
            "top_p": 0.8,
            "stop": [
                "<|im_end|>",
                "<|im_start|>"
            ]
        }, ensure_ascii=False)
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    response = requests.request("POST", url, data=payload, timeout=3000, headers=headers)
    if response.status_code != 200: raise Exception(response.text)
    result = json.loads(response.text)
    result = result['choices'][0]['message']['content']
    if record_time: return result, time.time()-start
    return result

#@staticmethod
def get_api_by_name(model_name:str, **api_params):
    if model_name.lower() == 'DeepSeek-V3'.lower():
        return deepseek_v3_api
    elif model_name.lower() == 'Qwen-Instruct-API'.lower():
        return partial(qwen_instruct_third_api, **api_params)
    elif model_name.lower() == 'DeepSeek-R1'.lower():
         return deepseek_r1_api
    elif model_name.lower() == 'DouBao-1.5Pro-32K'.lower():
        return doubao_15_pro_32k_api
    elif model_name.lower() == 'vllm'.lower():
        return partial(get_vllm_model_api, **api_params)
    else:
        print(f'Model `{model_name}` is not implemented yet. And will use `Doubao-1.5-Pro` by default.')


if __name__ == '__main__':
    from rich.progress import Progress
    import re
    
    sysp = open('./sysp.md', 'r', encoding='utf-8').read()
    usrp = open('./usrp.md', 'r', encoding='utf-8').read()
    
    # with Progress() as progress:
    #     task = progress.add_task("[red]🧐 Thinking...", total=None)
    #     func = get_api_by_name('vllm', version='MiniMax-M2')
    #     ans, time_cost =  func(usrp, system_prompt=sysp, record_time=True)
    #     # 从markdown文本中解析html代码
    #     pattern = r'```html\s*(.*?)\s*```'
    #     html_code = re.findall(pattern, ans, re.DOTALL)[0]
    #     with open('./ai timer/ai_timer_output-minimax-m2.html', 'w', encoding='utf-8') as f:
    #         f.write(html_code)
    # print(f'✅ Html文件已生成完毕\n⏱️ Time cost: {time_cost:.3f}s')
    # print('👉 请打开 `ai_timer_output.html` 文件查看结果')
    
    
    # qwen3-max
    # qwen3-coder-plus
    # qwen3-vl-plus
    with Progress() as progress:
        task = progress.add_task("[red]🧐 Thinking...", total=None)
        version = 'qwen3-coder-plus'
        func = get_api_by_name('Qwen-Instruct-API', version=version)
        # ans, time_cost = func('你是谁？你的版本信息是什么？', record_time=True)
        ans, time_cost = func(usrp, system_prompt=sysp, record_time=True)
        # 从markdown文本中解析html代码
        pattern = r'```html\s*(.*?)\s*```'
        html_code = re.findall(pattern, ans, re.DOTALL)[0]
        with open(f'./ai_timer_output-{version}.html', 'w', encoding='utf-8') as f:
            f.write(html_code)
    print(f'✅ Html文件已生成完毕\n⏱️ Time cost: {time_cost:.3f}s')
    print('👉 请打开 `ai_timer_output.html` 文件查看结果') 
