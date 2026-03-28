---
title: AutoResearch Agent
date: 2026-03-28
order: 1
summary: 一些使用autoresearch的思考（持续更新）
tags: AutoResearch Agent
---

## Why AutoResearch?
回顾近年来LLM的质变，一大部分原因是因为RLVR，即带有可验证的reward的RL使得整体泛化性以及数据利用率等得到了质变。

<br>

**何为可验证的reward?**

1. 数学题的答案是否匹配
2. 代码的结果是否正确
3. 代码是否通过编译
4. 一个问答题的回答是否等于预设的答案
5. ...

<br>

现阶段带有旗舰模型的Agent，如Claude Code、Codex已经具备极强的autoresearch能力。即给定一个明确的目标，可以24小时不间断地进行research。

<br>

下面是为什么我开始进行尝试的原因：
1. 最近着手一个性能优化的项目，发现其实性能优化的指标其实是一个pair-wise的可对比可比较的指标，这个其实天然是一个可验证的指标，和LLM的RL的目标相匹配，从理论上讲LLM天然适合解决这种问题。
2. 我尝试过几天手动对codex进行prompt生成优化代码，然后手动验证，效率极低，一下午只能做个位数个实验。其实很明显，无论是生成优化代码还是验证代码，一切瓶颈都在我自己本身。而这些天然适合Agent自己来做。
3. karpathy的autoresearch项目的成功确确实实给了我一些灵感。

## Let's Get Started!
以codex为例，我们需要定义好AGENTS.md文件。但是，“定义好”是一个很模糊的概念，是一个带有偏好的概念。

<br>

下面列举一些我认为好的“AGENTS.md”应该包含的内容：
1. 项目简介
2. 项目最终目标（对应RL的一个可验证的task）
3. 个人思考，有条件可以给出初步解决方案（一个更好的优化起点，对应RL所需的一个好的SFT的checkpoint）
4. 环境准备相关的脚本、命令、数据集准备等到（环境上的constraints）
5. 明确Agents的constraints（明确Agents能做的事以及不能做的事，对应一个笼统的RL的action space）
6. 实验过程相关数据和文档的维护（实验数据、方案的持久化，AGENTS.md文档的维护方式，一些成功、失败经验的维护方式），为了long term运行做准备
7. 注意事项（这里发挥空间比较大，因为action space特别大以及AGENTS.md不可能完美，需要根据实际情况不断做出提醒和限制）

## 一些有趣的坑
一个针对可验证reward的long term的agent简直和RL一摸一样，有一样的老毛病：**reward hacking**!!!

<br>

举一个例子，假设reward或者目标是将整体性能提高20%，但是其实项目目的是为了证明**某个模块的优化**可以起到整体性能提高20%的效果。但是Agent会通过优化**其他模块**的性能来达成整体的目的，这就导致了某种程度上的reward hacking。因为baseline是不采用任何优化，所以性能提高都源于通用优化。

<br>

下面是一些思考和归因：
1. 在这种场景下，可能是需要定义bounded reward（但不一定容易实现，由于有些有不是绝对数值的reward，而是相对的值）
2. AGENTS.md由于是人编写的，会有各种问题，容易被找到漏洞
3. 由于reward hacking，导致实验不公平，导致性能提升的原因未来源于预设的目的。从而浪费大量时间和token

<br>

一些解决方案：
1. AGENTS.md中明确指出避免reward hacking，给出few-shot来避免这种情况
2. 还是需要人偶尔看下Agent的实验思路，看有没有偏，有没有发生reward hacking
3. AGENTS.md需要进行头脑风暴，尽量提前避免这种情况
4. 可能可以写一个通用的anti reward hacking的skill来解决这个问题（通用性还是难定义的）

## 总结
最近明确感受到瓶颈在自己以及自己的钱包。但是想法还是很重要的。此外，很多可验证项目都可以试试autoresearch的思路。Agent Reward Hacking甚至适合当一个research topic来解决。
