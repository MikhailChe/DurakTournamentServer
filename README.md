# Турнирный сервер по игре "Дурак"

Карточная игра "Дурак" 1х1

Есть колода
В начале игры раздаётся по 6 карт
Игроки ходят по очереди. Серия из 10 матчей. Игру начинает игрок с самой младщей картой козырей.

Во время игры игрокам передаётся состояние игры в виде набора карт игрока, количества карт соперника, количества карт в колоде (с учётом козырной карты), козырной карты (при её наличии в колоде), передаются пары карт на поле.
Игра в подкидного дурака, без переводов.

Действия игрока:
* Игрок который ходит
	* Сходить определённой картой
	* Подкинуть карту
	* Объявить отбой
* Игрок который отбивается
	* Отбиться определённой картой
	* Сдаться при невозможности отбиться или по тактическим соображениям

Порядок игры с точки зрения сервера:
Игроки регистрируются в систеаме, получая токен для игры. Далее они используют этот токен, чтобы пинговать сервис один раз в секнунду на наличие готовой пары игры. login/get-token?login=login&password=password
Из пула подключенных игроков собирается пара.
Игра инициализируется, карты раздаются игрокам. 
Игроки узнают о том что игра собралась из ручки game/my-games-list?token=token
Игроки получают начальное состояние игрового поля. Игрок который должен ходить получает в сообщении состояние "разрешено ходить", игрок который ожидает хода получает состояние "ожидаем хода другого игрока".
Игрок, который должен сходить обращается к ручке game/play/<<game-id>>/makemove/?token=token&action=put/endturn/loose&card=5C
Сервер проверяет есть ли игра с таким game-id, проверяет зарегистрирован ли пользователь с таким token в этой игре, проверяет может ли игрок выполнять действия сейчас и можно ли выполнить это действие в таком состоянии. Ответ - успех или отказ в действии и новое текущее состояние игрового поля.

Возможна отдельная блокирующая ручка, которая ожидает когда ход игры перейдёт другому игроку. Так чтобы можно было не поллить, а просто ждать ответа от сервера. game/play/<<game-id>>/waitmyturn?token=token

Не забываем профилировать каждого игрока и логировать все действия игроков для анализа игры.
