# Shoploop AI — Codex 视频技能 / Codex Video Skills

无水印视频生成的 Codex Agent Skills。装进 Codex 后,直接用自然语言让它出片。
White-label Codex agent skills for no-watermark video generation — install once, then ask Codex in plain language to make videos.

技能 / Skills: `shoploop-video`(出片 / generate)、`shoploop-setup`(装与自检 / install + self-check)。

> Windows 用户把命令里的 `python3` 换成 `python` 或 `py -3`。On Windows use `python` or `py -3` instead of `python3`.

## 1. 安装 / Install

需要 Node.js(`npx` 随 npm 提供)。Requires Node.js (`npx` ships with npm).

```bash
# 装进当前项目 / install into the current project
npx skills add shoploopai/shoploop-skills --all

# 或只装指定技能 / or pick specific skills
npx skills add shoploopai/shoploop-skills --skill shoploop-video --skill shoploop-setup

# 全局安装,所有项目可用 / global install, available everywhere
npx skills add shoploopai/shoploop-skills --all -g
```

技能装进 Codex 的 `.agents/skills/`(项目)或全局技能目录。装完**新开一个 Codex 会话**,`/skills` 里就能看到。
Skills land in Codex's `.agents/skills/` (project) or the global skills dir. **Start a new Codex session** after install; they then appear in `/skills`.

## 2. 配置 Key / Configure

在项目根创建 `.env.shoploop`(或跑 `shoploop-setup` 自动生成模板):
Create `.env.shoploop` in your project root (or run `shoploop-setup` to generate the template):

```bash
SHOPLOOP_KEY=sk-your-customer-key
SHOPLOOP_BASE=https://seedance.shoploopai.com
SHOPLOOP_MODEL=seedance2.0
```

不要提交 `.env.shoploop`;`shoploop-setup` 会自动把它加进 `.gitignore`。
Do not commit `.env.shoploop`; `shoploop-setup` adds it to `.gitignore` for you.

## 3. 使用 / Use

直接对 Codex 说:"帮我生成一个 9:16 的产品展示视频,5 秒,电影感,下载到 shoploop_outputs/demo.mp4"。
Just tell Codex: "Make a 9:16 cinematic product video, 5 seconds, save to shoploop_outputs/demo.mp4." Codex auto-selects `shoploop-video`, or type `$shoploop-video`.

时长 4–15 秒;生成通常需要几分钟。Duration 4–15s; rendering usually takes a few minutes.

## 更新 / Update

```bash
npx skills update
```
