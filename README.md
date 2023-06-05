
# Manual bridger
<a href="https://ibb.co/jvqh3JV"><img src="https://i.ibb.co/5WCTsKY/manual.png" alt="manual" border="0">

Ручной режим, в котором все акки прогонит с выставленными настройками.
## Функционал (manual bridger)

 - Поддерживаемые сети: *Arbitrum, Optimism, Avalanche, BSC, Ethereum (mainnet), Polygon, Fantom, CoreDao*
 - Поддерживаемые мосты: *Stargate, Core, Aptos (btc.b, harmony will be included in next updates)*
 - Поддерживаемы токены для бриджа: *USDC, USDT, Ethereum (STG, btc.b  will be included in next updates)*
 - Возможность бриджить USDC → USDT и обратно, если нет ликвидности и если это позволяет мост.
 - Возможность бриджа на один адрес (если вам все равно на связи м/у кошельками). В случае с аптосом, для каждого евм кошелька нужна пара аптос кошелька в файле `aptos_addresses.txt`, если не хотите бриджить на один кошелёк.
 - Возможность бриджа всего баланса в токенах
 - Настройка задержки между аккаунтами (кошельками) в выбранном диапазоне, выбирается рандомно между *value1 и value2*
 - Проверка и авто аппрув токенов на бридж.
## Настройка (manual bridger)
 Запуск скрипта возможен возможен через gui интерфейс, либо же напрямую с настройками из конфиг файла `config_manual.yaml`. Настройки в обоих случая идентичные.
 
 - **Coin to transfer - Coin to receive** - выбор пары для бриджа, полезно когда в определенной паре нет ликвидности. Перед настройкой стоит проверить доступен ли бридж в такой паре.
 - **Address to send** - опциональный выбор, если хотите со всех мультов бриджить на один кошель. Можно вписать евм адрес или аптос, если бриджите в него.
 - **Min amount и max amount to bridge** - диапазон в котором рандомно выберется сумма для бриджа. Если не нужен рандом, то просто укажите в оба поля одинаковые значения. 
 - **Send all balance** - при активированном чек боксе будет бриджить весь доступный баланс кошелька в выбранных токенах.
 - **Slippage** - Выбор слиппажа в процентах (Пример: 0.5 = 0.5%)
 - **Gas limit** - под каждую сеть нужен разный газ лимит, но можете поставить заранее большое значение, в конечном итоге через gas_estimate будет использоваться требуемое сетью значение
 - **Gas price** - по дефолту стоит автоматический, но если сеть в моменте нагружена может сыпать ошибки, так что можно выбрать вручную.
 - **Min delay и max delay (sec)** - диапозон в котором рандомно выберется значение задержки (в секундах) между бриджей кошельков.
 - **Test mode** - Можно запустить в тестовом режиме, скрипт проверит корректность транзы и покажет estimate gas
## Warmup Bridger
<a href="https://imgbb.com/"><img src="https://i.ibb.co/vJjMt3h/auto-menu.png" alt="auto-menu" border="0"></a>

Режим прогрева, скрипт сам выберет из указанных вами сетей две рандомные в которых будет бриджить. Для каждого кошелька он будет выбирать рандомный путь, в зависимости от наличия баланса в указанном диапазоне бриджа *min и max amount to bridge*.
## Функционал (warmup bridger)
 - Поддерживаемые сети: *Arbitrum, Optimism, Avalanche, BSC,  Ethereum (mainnet), Polygon, Fantom*
 - Бридж происходит только через *Stargate*
 - Парсинг баланса кошелька в указанных сетях, исходя из балансов выберется рандомная *source* сеть
 - Запись логов каждого кошелька с данными о последнем действии в папке `wallet_logs`
 - Проверка и авто аппрув токенов на бридж.
## Настройка (warmup bridger)
 - **Select chains** - нужно указать сети в которых будет происходить прогрев, нужно указать минимум 2 сети.
 - **Coin to transfer** - Можно выбрать между *Ethereum* и *Stablecoins*(USDC, USDT в зависимости от доступности монеты в конкретной сети)
 - **Min delay и max delay (sec)** - диапозон в котором рандомно выберется значение задержки (в секундах) между бриджей кошельков.
- **Min amount и max amount to transfer** - диапазон в котором рандомно выберется сумма для бриджа. Если не нужен рандом, то просто укажите в оба поля одинаковые значения. Если максимальное значение окажется больше баланса кошелька, то за *max amount to transfer* будет принят баланс кошелька.
- **Send all balance** - бридж всего баланса, нужно указать *Min amount*, порог с которого будет учитываться баланс в сети при подборе пути бриджа.
- **Max gas limit** - максимальный газ лимит. Общий для всех сетей, поэтому можете выставить наибольшее значение, выберется актуальное в каждой сети через `estimate_gas`
-  **Slippage** - Выбор слиппажа в процентах (Пример: 0.5 = 0.5%)
- **Shuffle wallets** - рандомизация порядка выбора кошельков из файла
- **Test mode** - Можно запустить в тестовом режиме, скрипт проверит корректность транзы и покажет estimate gas.
## STG staker
<a href="https://imgbb.com/"><img src="https://i.ibb.co/f40s4yG/stg-staker.png" alt="stg-staker" border="0"></a>

Локап и стейк стг в указанных ниже сетях, за это вам дается veSTG, которые нужны для голосования в ДАО
## Функционал (STG staker)
 - Поддерживаемые сети: *Arbitrum, Avalanche, BSC, Polygon, Fantom*
 - Период лока (1-36 мес)
## Настройка (STG staker)
- **Source chain** - сеть в которой будет локаться в стейк STG
- **Min stake smount и max stake amount** - диапазон в котором рандомно выберется сумма для стейка. Если не нужен рандом, то просто укажите в оба поля одинаковые значения. Если максимальное значение окажется больше баланса кошелька, то за *max amount to transfer* будет принят баланс кошелька.
- **Stake all balance** - стейк всего доступного количество STG на кошельке
- **Lock period** - период лока токенов, в диапазоне 1-36 мес.
-  **Min delay и max delay (sec)** - диапозон в котором рандомно выберется значение задержки (в секундах) между кошельками.
- **Max gas limit** - максимальный газ лимит. Общий для всех сетей, поэтому можете выставить наибольшее значение, выберется актуальное в каждой сети через `estimate_gas`
- **Test mode** - Можно запустить в тестовом режиме, скрипт проверит корректность транзы и покажет estimate gas.
- 
## Liquidity adder
<a href="https://imgbb.com/"><img src="https://i.ibb.co/0J9dsBH/liquidity-adder.png" alt="liquidity-adder" border="0"></a>

Добавление ликвидности в пулы USDC или USDT в указанных ниже сетях. 
P.S. В функционале только добавление ликвидности, в фарм лп токены не кидаются!
## Функционал (STG staker)
 - Поддерживаемые сети: *Arbitrum, Avalanche, BSC, Polygon, Fantom, Optimism*

## Настройка (STG staker)
- **Source chain** - сеть в которой будет добавляться ликвидность
- **Coin to add liquidity** - токен для добавления ликвидности
- **Min liq mount и max liq amount** - диапазон в котором рандомно выберется сумма для добавления ликвидности. Если не нужен рандом, то просто укажите в оба поля одинаковые значения. Если максимальное значение окажется больше баланса кошелька, то за *max amount to transfer* будет принят баланс кошелька.
-  **Min delay и max delay (sec)** - диапозон в котором рандомно выберется значение задержки (в секундах) между кошельками.
- **Max gas limit** - максимальный газ лимит. Общий для всех сетей, поэтому можете выставить наибольшее значение, выберется актуальное в каждой сети через `estimate_gas`
- **Test mode** - Можно запустить в тестовом режиме, скрипт проверит корректность транзы и покажет estimate gas.

## Настройка RPC
Все rpc url находятся в  `contracts/rpcs.json`, где их можно изменить/поменять. Для каждой сети можно добавить несколько рпс, через запятую.

 Перед запуском все rpc пингануться, так что для каждой сети нужно предоставить минимум один рабочий rpc url.
## Wallets
Все адреса и приватники вставляем в файл с новой строки. Все файлы создавать в главной директории.

-   Приватники от evm кошельков закидываем в файл  `evm_wallets.txt`  (формат только 0х...)
    
-   Адреса aptos кошельков (для aptos bridge) в файл  `aptos_addresses.txt`
    
P.S. Количество аптос и евм кошельков должно быть одинаковым, если вам нужно чтобы каждый евм адресс бриджил на отдельный аптос кошелёк.
## Запуск и использование
Перед запуском через pip устанавливаем необходимые библиотеки:

    pip install -r req.txt
  Запуск через интерфейс происходит через файл `run_gui.py`:
  

    python run_gui.py

  
Все конфиги для настройки находятся в папке `config`:

`config_liquidity.yaml` - конфиг для **Liquidity adder**
`config_manual.yaml` - конфиг для **Manual bridger**
`config_stake_stg.yaml` - конфиг для **STG staker**
`config_warmup.yaml` - конфиг для **Warmup bridger**

Файлы для запуска напрямую с настройками с конфиг файла находятся в папке `run scripts`:
`run_liquidity_adder.py` - run файл для **Liquidity adder**
`run_manual_bridger.py` - run файл для **Manual bridger**
`run_stg_staker.py` - run файл для  **STG staker**
`run_autobridge.py` - run файл для **Warmup bridger**


