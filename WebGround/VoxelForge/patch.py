import sys

path = '/Users/cielevel/ProjectAI/AxuPlayground/WebGround/VoxelForge/VoxelForgeV2.html'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. API Layer
api_layer_start = text.find('// ======================== AI API LAYER ========================')
api_layer_end = text.find('// ======================== APP STATE ========================')

new_api_layer = """// ======================== AI API LAYER ========================
        const PROVIDERS = {
            openai: {
                name: 'OpenAI',
                defaultBaseUrl: 'https://api.openai.com',
                buildRequest(stage, apiKey, model, prompt, extraData, baseUrl, complexity, maxSize) {
                    const url = `${baseUrl || this.defaultBaseUrl}/v1/chat/completions`;
                    const sysPrompt = stage === 1 ? buildShapeSystemPrompt(complexity, maxSize) : buildColorSystemPrompt(complexity, maxSize);
                    const userPrompt = stage === 1 ? buildShapeUserPrompt(prompt) : buildColorUserPrompt(prompt, extraData);
                    return {
                        url,
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${apiKey}`
                        },
                        body: {
                            model,
                            messages: [
                                { role: 'system', content: sysPrompt },
                                { role: 'user', content: userPrompt }
                            ],
                            temperature: 0.7,
                            response_format: { type: 'json_object' }
                        }
                    };
                },
                parseResponse(data) {
                    const text = data.choices?.[0]?.message?.content || '';
                    return extractJsonObject(text);
                }
            },
            claude: {
                name: 'Claude',
                defaultBaseUrl: 'https://api.anthropic.com',
                buildRequest(stage, apiKey, model, prompt, extraData, baseUrl, complexity, maxSize) {
                    const url = `${baseUrl || this.defaultBaseUrl}/v1/messages`;
                    const sysPrompt = stage === 1 ? buildShapeSystemPrompt(complexity, maxSize) : buildColorSystemPrompt(complexity, maxSize);
                    const userPrompt = stage === 1 ? buildShapeUserPrompt(prompt) : buildColorUserPrompt(prompt, extraData);
                    return {
                        url,
                        headers: {
                            'Content-Type': 'application/json',
                            'x-api-key': apiKey,
                            'anthropic-version': '2023-06-01',
                            'anthropic-dangerous-direct-browser-access': 'true'
                        },
                        body: {
                            model,
                            max_tokens: 16384,
                            system: sysPrompt,
                            messages: [
                                { role: 'user', content: userPrompt }
                            ]
                        }
                    };
                },
                parseResponse(data) {
                    const text = data.content?.[0]?.text || '';
                    return extractJsonObject(text);
                }
            },
            glm: {
                name: 'GLM',
                defaultBaseUrl: 'https://open.bigmodel.cn',
                buildRequest(stage, apiKey, model, prompt, extraData, baseUrl, complexity, maxSize) {
                    const url = `${baseUrl || this.defaultBaseUrl}/api/paas/v4/chat/completions`;
                    const sysPrompt = stage === 1 ? buildShapeSystemPrompt(complexity, maxSize) : buildColorSystemPrompt(complexity, maxSize);
                    const userPrompt = stage === 1 ? buildShapeUserPrompt(prompt) : buildColorUserPrompt(prompt, extraData);
                    return {
                        url,
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${apiKey}`
                        },
                        body: {
                            model,
                            messages: [
                                { role: 'system', content: sysPrompt },
                                { role: 'user', content: userPrompt }
                            ],
                            temperature: 0.7
                        }
                    };
                },
                parseResponse(data) {
                    const text = data.choices?.[0]?.message?.content || '';
                    return extractJsonObject(text);
                }
            },
            deepseek: {
                name: 'DeepSeek',
                defaultBaseUrl: 'https://api.deepseek.com',
                buildRequest(stage, apiKey, model, prompt, extraData, baseUrl, complexity, maxSize) {
                    const url = `${baseUrl || this.defaultBaseUrl}/v1/chat/completions`;
                    const sysPrompt = stage === 1 ? buildShapeSystemPrompt(complexity, maxSize) : buildColorSystemPrompt(complexity, maxSize);
                    const userPrompt = stage === 1 ? buildShapeUserPrompt(prompt) : buildColorUserPrompt(prompt, extraData);
                    return {
                        url,
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${apiKey}`
                        },
                        body: {
                            model,
                            messages: [
                                { role: 'system', content: sysPrompt },
                                { role: 'user', content: userPrompt }
                            ],
                            temperature: 0.7
                        }
                    };
                },
                parseResponse(data) {
                    const text = data.choices?.[0]?.message?.content || '';
                    return extractJsonObject(text);
                }
            },
            gemini: {
                name: 'Gemini',
                defaultBaseUrl: 'https://generativelanguage.googleapis.com',
                buildRequest(stage, apiKey, model, prompt, extraData, baseUrl, complexity, maxSize) {
                    let urlBase = baseUrl || this.defaultBaseUrl;
                    if (urlBase.endsWith('/')) urlBase = urlBase.slice(0, -1);
                    const url = `${urlBase}/v1beta/models/${model}:generateContent?key=${apiKey}`;
                    const sysPrompt = stage === 1 ? buildShapeSystemPrompt(complexity, maxSize) : buildColorSystemPrompt(complexity, maxSize);
                    const userPrompt = stage === 1 ? buildShapeUserPrompt(prompt) : buildColorUserPrompt(prompt, extraData);
                    return {
                        url,
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: {
                            system_instruction: {
                                parts: { text: sysPrompt }
                            },
                            contents: [
                                { parts: [{ text: userPrompt }] }
                            ],
                            generationConfig: {
                                responseMimeType: 'application/json',
                                temperature: 0.7
                            }
                        }
                    };
                },
                parseResponse(data) {
                    const text = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
                    return extractJsonObject(text);
                }
            }
        };

        function buildShapeSystemPrompt(complexity = 300, maxSize = 32) {
            const minVoxels = Math.max(10, Math.floor(complexity * 0.8));
            const maxVoxels = Math.floor(complexity * 1.2);
            return `You are a 3D voxel shape generator. Your output must be ONLY a valid JSON object.
Rules:
- Generate an array of 3D integer coordinates representing the shape blocks.
- Keep the voxel count between ${minVoxels} and ${maxVoxels}. Target: ${complexity} voxels.
- Coordinates must fit within a box: -${maxSize} to ${maxSize}.
- Center the model around x=0, z=0. The bottom starts at y=0.
- Output MUST be a JSON object with a key "voxels", containing an array of coordinates [x, y, z].
Example: {"voxels": [[0,0,0], [1,0,0], [0,1,0]]}`;
        }

        function buildShapeUserPrompt(prompt) {
            return `Generate the voxel shape coordinates for: "${prompt}". Return ONLY the JSON object.`;
        }

        function buildColorSystemPrompt(complexity = 300, maxSize = 32) {
            return `You are a 3D voxel coloring AI. Your output must be ONLY a valid JSON object.
Rules:
- You will receive a prompt and a list of voxel coordinates.
- You must generate a hex color for each coordinate to paint the model.
- Return a JSON object with a "colors" key.
- The value must be an object mapping the coordinate string "[x,y,z]" to a hex color "#RRGGBB".
Example: {"colors": {"[0,0,0]": "#FF0000", "[1,0,0]": "#00FF00"}}`;
        }

        function buildColorUserPrompt(prompt, extraData) {
            return `Color the voxel model for: "${prompt}".
Coordinates:
${JSON.stringify(extraData)}
Return ONLY the JSON object mapping coordinates to colors.`;
        }

        function extractJsonObject(text) {
            let cleaned = text.trim();
            cleaned = cleaned.replace(/```(?:json)?\s*/gi, '').replace(/```/g, '').trim();
            const startIdx = cleaned.indexOf('{');
            if (startIdx === -1) throw new Error('No JSON object found in response');
            cleaned = cleaned.substring(startIdx);
            try { return JSON.parse(cleaned); } catch (e) {
                const endIdx = cleaned.lastIndexOf('}');
                if (endIdx > 0) {
                    try { return JSON.parse(cleaned.substring(0, endIdx + 1)); } catch (e2) {}
                }
            }
            throw new Error('无法解析阶段 JSON');
        }

        function extractJsonArray(text) {
            let cleaned = text.trim();
            cleaned = cleaned.replace(/```(?:json)?\s*/gi, '').replace(/```/g, '').trim();
            const startIdx = cleaned.indexOf('[');
            if (startIdx === -1) throw new Error('No JSON array found in response');
            cleaned = cleaned.substring(startIdx);
            try { return JSON.parse(cleaned); } catch (e) {
                const endIdx = cleaned.lastIndexOf(']');
                if (endIdx > 0) {
                    try { return JSON.parse(cleaned.substring(0, endIdx + 1)); } catch (e2) {}
                }
            }
            throw new Error('无法解析 JSON 数组');
        }

        function parseVoxelData(rawArray) {
            return rawArray.map(v => {
                let colorVal = v.color || v.c || '#CCCCCC';
                let colorInt = 0xCCCCCC;
                if (typeof colorVal === 'string') {
                    if (colorVal.startsWith('#')) colorVal = colorVal.substring(1);
                    colorInt = parseInt(colorVal, 16);
                } else if (typeof colorVal === 'number') {
                    colorInt = colorVal;
                }
                return {
                    x: Math.round(Number(v.x) || 0),
                    y: Math.round(Number(v.y) || 0),
                    z: Math.round(Number(v.z) || 0),
                    color: isNaN(colorInt) ? 0xCCCCCC : colorInt
                };
            });
        }
        
"""

text = text[:api_layer_start] + new_api_layer + text[api_layer_end:]

# 2. testApi Overwrite array
test_api_target = """                const req = prov.buildRequest(config.key, config.model, 'Say "hello" in one word.', config.baseUrl);
                // Overwrite body to be minimal for test
                if (provider === 'claude') {
                    req.body.messages = [
                        { role: 'user', content: 'Reply with exactly one word: hello' }
                    ];
                    req.body.max_tokens = 32;
                    delete req.body.system;
                } else if (provider === 'gemini') {
                    req.body.contents = [{ parts: [{ text: 'Reply with exactly one word: hello' }] }];
                    delete req.body.system_instruction;
                    delete req.body.generationConfig;
                } else {
                    req.body.messages = [
                        { role: 'user', content: 'Reply with exactly one word: hello' }
                    ];
                    delete req.body.response_format;
                }"""

test_api_new = """                const req = prov.buildRequest(1, config.key, config.model, 'Say "hello" in one word.', null, config.baseUrl, 50, 32);
                // Overwrite body to be minimal for test
                if (provider === 'claude') {
                    req.body.messages = [
                        { role: 'user', content: 'Reply with exactly one word: hello' }
                    ];
                    req.body.max_tokens = 32;
                    delete req.body.system;
                } else if (provider === 'gemini') {
                    req.body.contents = [{ parts: [{ text: 'Reply with exactly one word: hello' }] }];
                    delete req.body.system_instruction;
                    delete req.body.generationConfig;
                } else {
                    req.body.messages = [
                        { role: 'user', content: 'Reply with exactly one word: hello' }
                    ];
                    delete req.body.response_format;
                }"""

text = text.replace(test_api_target, test_api_new)

# 3. generate function
generate_start = text.find('        async function generate() {')
generate_end = text.find('        // ======================== BOOT ========================')

generate_new = """        async function generate() {
            const prompt = document.getElementById('prompt-input').value.trim();
            if (!prompt || isGenerating) return;

            const config = getProviderConfig(activeProvider);
            if (!config.key) {
                showToast('请先配置 API Key（点击左上角 ⚙️）', 'error');
                toggleSettings();
                return;
            }

            isGenerating = true;
            document.getElementById('btn-generate').disabled = true;
            setGeneratingUI(true, `${PROVIDERS[activeProvider].name} 正在生成第一阶段(白模)...`);
            setConsoleLive(true);

            if (!document.getElementById('console-panel').classList.contains('open')) {
                toggleConsole();
            }

            logToConsole(`━━━ 新生成任务(分步生成) ━━━`, 'info');
            logToConsole(`提供商: ${PROVIDERS[activeProvider].name}`, 'info');
            logToConsole(`模型: ${config.model}`, 'info');
            logToConsole(`提示词: "${prompt}"`, 'info');

            const startTime = Date.now();
            const complexity = parseInt(document.getElementById('param-complexity').value) || 300;
            const maxSize = parseInt(document.getElementById('param-max-size').value) || 32;

            try {
                const provider = PROVIDERS[activeProvider];
                
                // ===== STAGE 1: SHAPE =====
                const req1 = provider.buildRequest(1, config.key, config.model, prompt, null, config.baseUrl, complexity, maxSize);
                logToConsole(`[阶段一] 发送形状请求...`, 'data');
                
                const resp1 = await fetch(req1.url, {
                    method: 'POST', headers: req1.headers, body: JSON.stringify(req1.body)
                });
                
                if (!resp1.ok) {
                    const errText = await resp1.text();
                    throw new Error(`阶段一 API 失败 (${resp1.status})`);
                }
                
                const data1 = await resp1.json();
                const shapeResult = provider.parseResponse(data1);
                
                if (!shapeResult || !shapeResult.voxels || !Array.isArray(shapeResult.voxels)) {
                    throw new Error('阶段一未返回有效的体素数组 (voxels)');
                }
                
                const coords = shapeResult.voxels;
                logToConsole(`[阶段一] 成功生成 ${coords.length} 个白模坐标 (${Date.now() - startTime}ms)`, 'success');
                if (coords.length === 0) throw new Error('AI 返回了空的形状');
                
                // 暂时渲染白模
                const whiteModelData = coords.map(c => ({
                    x: c[0], y: c[1], z: c[2], color: 0xF0F0F0
                }));
                engine.loadModel(whiteModelData);
                document.getElementById('voxel-count').textContent = coords.length;
                
                // ===== STAGE 2: COLOR =====
                setGeneratingUI(true, `${PROVIDERS[activeProvider].name} 正在生成第二阶段(着色)...`);
                logToConsole(`[阶段二] 发送颜色映射请求...`, 'data');
                updateGenStatus('正在生成第二阶段(着色)...');
                
                const req2 = provider.buildRequest(2, config.key, config.model, prompt, coords, config.baseUrl, complexity, maxSize);
                
                const resp2 = await fetch(req2.url, {
                    method: 'POST', headers: req2.headers, body: JSON.stringify(req2.body)
                });
                
                if (!resp2.ok) {
                    const errText = await resp2.text();
                    throw new Error(`阶段二 API 失败 (${resp2.status})`);
                }
                
                const data2 = await resp2.json();
                const colorResult = provider.parseResponse(data2);
                
                if (!colorResult || !colorResult.colors) {
                    throw new Error('阶段二未返回有效的颜色映射 (colors)');
                }
                
                const colorMap = colorResult.colors;
                logToConsole(`[阶段二] 接收到着色数据 (${Date.now() - startTime}ms)`, 'success');
                
                // ===== ASSEMBLE =====
                updateGenStatus('正在渲染最终模型...');
                const finalVoxels = coords.map(c => {
                    const key1 = `[${c[0]},${c[1]},${c[2]}]`;
                    const key2 = `[${c[0]}, ${c[1]}, ${c[2]}]`;
                    let hexStr = colorMap[key1] || colorMap[key2] || '#CCCCCC';
                    if (hexStr.startsWith('#')) hexStr = hexStr.substring(1);
                    
                    return {
                        x: Math.round(Number(c[0]) || 0),
                        y: Math.round(Number(c[1]) || 0),
                        z: Math.round(Number(c[2]) || 0),
                        color: parseInt(hexStr, 16) || 0xCCCCCC
                    };
                });
                
                engine.loadModel(finalVoxels);
                document.getElementById('voxel-count').textContent = finalVoxels.length;

                const elapsedTotal = Date.now() - startTime;
                logToConsole(`✅ 生成完成！共 ${finalVoxels.length} 个体素，总耗时 ${elapsedTotal}ms`, 'success');
                showToast(`✨ 生成了 ${finalVoxels.length} 个体素`, 'success');
                
                document.getElementById('prompt-input').value = '';
                autoResizeTextarea(document.getElementById('prompt-input'));

            } catch (err) {
                const elapsed = Date.now() - startTime;
                logToConsole(`❌ 生成失败 (${elapsed}ms): ${err.message}`, 'error');
                showToast('生成失败: ' + err.message, 'error');
            } finally {
                isGenerating = false;
                document.getElementById('btn-generate').disabled = !document.getElementById('prompt-input').value.trim();
                setGeneratingUI(false);
                setConsoleLive(false);
            }
        }

"""
text = text[:generate_start] + generate_new + text[generate_end:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Patched successfully")
