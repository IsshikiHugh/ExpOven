# ExpOven

<center><img src="https://github.com/user-attachments/assets/c478b73c-4f7b-4b7d-bd26-28522892fb98"></center>

<center>

[🍞 Installation](#installation)
|
[🍕 Quick Start](#quick-start)
|
[🧅 Contribution](./docs/CONTRIBUTING.md)
</center>

ExpOven is a notifier application mainly designed for AI researchers. It provides a simple and efficient way to monitor the status of experiments opportunely.

You execute your experiments or commands on the server. When the command is completed or encounters an issue, you will receive a notification in your messaging apps (such as DingTalk, email, Slack, etc.). Additionally, you can use this tool to track the progress of the experiments.

## Installation

### Step 1. Install Package

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

### Step 2. Setup & Configuration

Now you need to configuration the third-party supports. You can only configure the most commonly used ones. Check the following links for more details:

- [DingTalk](./docs/third_party_setup/dingtalk.md)
- [Feishu(Lark)](./docs/third_party_setup/feishu.md)
- [Email](./docs/third_party_setup/email.md)

Next, you need to edit the local configuration file.

<details> <summary>📌 About Config File Location</summary>

> The configuration file will be created at `$OVEN_HOME/cfg.yaml`, the default value of `OVEN_HOME` is `~/.config/oven`.
>
> You can check the current `OVEN_HOME` through CLI `oven home`.
>
> To customize `OVEN_HOME`, you only need to set the environment variable `OVEN_HOME` to the desired path.
</details><br/>


```shell
oven init-cfg  # Configuration template will be created at $OVEN_HOME/cfg.yaml.
```

The template of the config file will be synced from [docs/cfg.yaml.temp](./docs/cfg.yaml.temp).


## Quick Start

Check [docs/examples.py](./docs/examples.py) for runnable examples.

### As CLI

```shell
ding [LOGGING MESSAGE]
# eg:
ding 'Hello World!'
mv from to ; ding 'Data moved.'  # Similar to `bake mv from to`.
```

Tips: When you have already started the experiment, you can still print type `ding 'Exp xxx stopped.'` and press Enter. Although it seems you don't send the command correctly, it's actually put into the queue. When the experiment is over, the command will still be executed.

<center><img src="docs/eg_ding_dingtalk.png" width="50%"></center>

```shell
bake [RUNNABLE COMMAND]
# eg:
bake echo 'Hello World!'
bake pip install -r requirements.txt
bake bash scripts/download_data.sh
bake CUDA_VISIBLE_DEVICES='0,1' python train.py
bake 'curl -X GET https://someweb.com/api?x=y'
# Tips: these two have different effects
X=1 bake "X=2 echo $X"  # outputs 1
X=1 bake 'X=2 echo $X'  # outputs 2
# Check 3.1.2.2 @ https://www.gnu.org/software/bash/manual/bash.html
```

<center><img src="docs/eg_bake_dingtalk.png" width="50%"></center>

### As Package

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

### Progress Tracking

Track progress with tqdm-like interface that also sends notifications:

```py
import oven

# Simple progress bar with notifications
for i in oven.progress_range(100, desc="Training"):
    train_step(i)

# Wrap any iterable
data = load_dataset()
for batch in oven.progress(data, desc="Processing batches"):
    process_batch(batch)

# Manual progress updates
with oven.ProgressBar(total=1000, desc="Custom task") as pbar:
    for i in range(100):
        do_work()
        pbar.update(10)  # Update by 10 items
```

Check [docs/pbar_interface.md](./docs/pbar_interface.md) for more information about the API.

## Contributing

Please check [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md) for more details.
