# ExpOven

<center><img src="https://github.com/user-attachments/assets/c478b73c-4f7b-4b7d-bd26-28522892fb98"></center>

<center>

[🍞 Installation](#installation)
|
[🔧 Configuration](#configuration)
|
[🍕 Usage](#usage)
|
[🧅 Contribution](./docs/CONTRIBUTING.md)
</center>

ExpOven is a notifier application mainly designed for AI researchers. It provides a simple and efficient way to monitor the status of experiments opportunely.

You execute your experiments or commands on the server. When the command is completed or encounters an issue, you will receive a notification in your messaging apps (such as DingTalk, email, Slack, etc.). Additionally, you can use this tool to track the progress of the experiments.

## Supported Backends

- [DingTalk](./docs/third_party_setup/dingtalk.md)
- [Feishu(Lark)](./docs/third_party_setup/feishu.md)
- [Slack](./docs/third_party_setup/slack.md)
- [Email](./docs/third_party_setup/email.md)

## Installation

Like most python packages, you can install ExpOven via following methods:

<details><summary>📌 Option 1. Install from PyPI. <b>[RECOMMENDED]</b></summary>

```shell
pip install exp-oven
```
</details>

<details><summary>📌 Option 2. Install from GitHub.</summary>

```shell
pip install git+https://github.com/IsshikiHugh/ExpOven
```
</details>

<details><summary>📌 Option 3. Install locally.</summary>

```shell
git clone https://github.com/IsshikiHugh/ExpOven.git
cd ExpOven
pip install .  # Make sure you are in the (virtual) environment that you want to install ExpOven.
```
</details><br/>

After installation, you can check if the installation is successful by typing the following command:

```shell
oven help
```

## Configuration

Now you need to configuration the third-party supports. You can only configure the most commonly used ones. Check the [Supported Backends](#supported-backends) section for setup guides.

```shell
oven init-cfg  # Creates config.yaml + ogroups/default.yaml under $OVEN_HOME.
```

<details> <summary>📌 About Config File Location</summary>

> The configuration files live under `$OVEN_HOME` (default `~/.config/oven`).
>
> ```
> ~/.config/oven
>    ├── config.yaml                   # meta config to set the default group
>    └── ogroups
>        ├── default.yaml              # default notification group (one or more backends)
>        └── <custom_group_name>.yaml  # customize other notification groups (one or more backends)
> ```
>
> You can check the current `OVEN_HOME` through CLI `oven home`.
>
> To customize `OVEN_HOME`, you only need to set the environment variable `OVEN_HOME` to the desired path.
</details><br/>

Edit `ogroups/default.yaml` to uncomment and fill in the backend(s) you want to use. A single group can contain multiple backends — all of them will be notified simultaneously.

<details> <summary>📌 Notification Groups (ogroups)</summary>

> Each YAML file under `ogroups/` defines a **notification group**. A group lists one or more backends that are all notified together.
>
> **Example** — `ogroups/work.yaml` with two backends:
> ```yaml
> backends:
>   - type: dingtalk
>     hook: https://oapi.dingtalk.com/robot/send?access_token=<?>
>     secure_key: <?>
>   - type: slack
>     hook: https://hooks.slack.com/services/<?>/<?>/<?>
> ```
>
> Set the default group: `oven set-default work`
>
> Or select per-command: `bake --ogroup work python train.py` or `ding -g work 'Hello World!'`
>
> In Python: `oven.toggle_ogroup('work')`
>
> List all groups: `oven list-ogroups`
</details><br/>

<details> <summary>📌 Migrating from v0.6.x</summary>

> If you are upgrading from ExpOven <= v0.6.4 (old single-file `cfg.yaml`), run the migration script:
>
> ```shell
> python scripts/migrate_config.py
> ```
>
> This converts your old config into the new layout, creating a group for each configured backend. The previously active backend becomes `ogroups/default.yaml`. The old file is backed up as `cfg.yaml.bak`.
</details><br/>

## Usage

Check [docs/examples/basic.py](./docs/examples/basic.py) for runnable examples.

### CLI

```shell
ding [--ogroup <group>] [LOGGING MESSAGE]
# eg:
ding 'Hello World!'
ding --ogroup work 'Hello World!'  # Use a specific group.
mv from to ; ding 'Data moved.'    # Similar to `bake mv from to`.
```

Tips: When you have already started the experiment, you can still print type `ding 'Exp xxx stopped.'` and press Enter. Although it seems you don't send the command correctly, it's actually put into the queue. When the experiment is over, the command will still be executed.

<center><img src="docs/eg_ding_dingtalk.png" width="50%"></center>

```shell
bake [--ogroup <group>] [RUNNABLE COMMAND]
# eg:
bake echo 'Hello World!'
bake --ogroup work python train.py  # Use a specific group.
bake pip install -r requirements.txt
bake bash scripts/download_data.sh
bake CUDA_VISIBLE_DEVICES='0,1' python train.py
CUDA_VISIBLE_DEVICES='0,1' bake python train.py
bake 'curl -X GET https://someweb.com/api?x=y'
# Tips: these two have different effects
X=1 bake "X=2 echo $X"  # outputs 1
X=1 bake 'X=2 echo $X'  # outputs 2
# Check 3.1.2.2 @ https://www.gnu.org/software/bash/manual/bash.html
```

<center><img src="docs/eg_bake_dingtalk.png" width="50%"></center>

### Python API

As a single function, it notifies the message. The two forms are equivalent.

```py
oven.notify('Hello World!')
oven.ding('Hello World!')

# eg:

def compute_loss(gt, pd):
    loss = (gt - pd).abs().mean()  # (,)
    if torch.isnan(loss).any():
        oven.notify('Loss contains NaN.')  # 👈
        ipdb.set_trace()
    return loss

def main():
    model = Model()
    train(model)
    metric = evaluate(model)
    oven.notify(f'Train over with metric: {metric}')  # 👈
```

As function wrapper, the notifier will be called both before and after the function is executed. The two forms are equivalent.

```py
@oven.monitor
def foo() -> None:
    print('Hello World!')

@oven.bake
def bar() -> None:
    print('Hello World!')

# eg:

@oven.monitor  # 👈
def train() -> None:
    for epoch in range(10):
        train_before_epoch()
        train_epoch()
        train_after_epoch()
```

You can switch the notification group for the current session:

```py
import oven
oven.toggle_ogroup('work')  # All subsequent calls use the 'work' group.
```

By default, it uses default group in the configuration file.

### Claude Code Skill

ExpOven ships a [Claude Code](https://claude.com/claude-code) skill at [`.claude/skills/notify/SKILL.md`](./.claude/skills/notify/SKILL.md) that gives the agent a `/notify` command backed by `ding`. Useful for letting Claude ping you when long-running tasks finish, with ExpOven routing the message to your configured platform(s).

<details><summary>📌 Install the skill</summary>

> **Project-local** (default): if you're working inside a clone of ExpOven, the skill is auto-discovered — no setup needed.
>
> **Global** (use from any project): copy or symlink the skill folder into your user-level skills directory.
> ```shell
> mkdir -p ~/.claude/skills
> cp -r .claude/skills/notify ~/.claude/skills/notify
> # or, to track upstream changes:
> ln -s "$(pwd)/.claude/skills/notify" ~/.claude/skills/notify
> ```
</details><br/>

```shell
/notify                       # sends "Task complete" via the saved ogroup
/notify Training finished     # sends that message
/notify --set-group work      # change the ogroup the skill routes to
/notify --show-group          # print the currently saved ogroup
/notify --reset-group         # forget; ask again on the next /notify call
```

The first time `/notify` is invoked it will ask which ogroup to use (picked from `oven list-ogroups`) and remember the choice in `${OVEN_HOME:-~/.config/oven}/claude-notify-group`.

## Contributing

Please check [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md) for more details.
