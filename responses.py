from random import choice, randint

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'Du bist aber still'
    elif 'hello' in lowered:
        return 'Hi'
    elif 'bye' in lowered:
        return 'bye'
    elif 'roll' in lowered:
        return f'Du rollst: {randint(1, 6)}'
    elif 'ping' in lowered:
        return 'pong'
    elif 'essen' in lowered:
        return 'Ich liebe Essen! Was isst du gerne?'
    elif 'urlaub' in lowered:
        return 'Urlaub klingt nach einer guten Idee. Wohin möchtest du reisen?'
    elif 'musik' in lowered:
        return 'Musik ist toll! Welche Art von Musik hörst du gerne?'
    elif 'film' in lowered:
        return 'Filme sind super! Welchen Film schaust du gerade?'
    elif 'hobby' in lowered:
        return 'Hobbies sind fantastisch! Was machst du in deiner Freizeit?'
    elif 'wetter' in lowered:
        return 'Das Wetter kann manchmal unberechenbar sein. Wie ist es bei dir gerade?'
    elif 'blood' in lowered:
        return 'Blood for the Blood God'
    elif 'khorne' in lowered:
        return 'Khorne cares not from whence the blood flows, only that it flows!'
    #elif '####' in lowered:
    #    return '####'
    #elif '####' in lowered:
    #    return '####'
    #elif '####' in lowered:
    #    return '####'
    #elif '####' in lowered:
    #    return '####'
    else:
        return choice(['Ich versteh dich nicht...',
                       'Worüber redest du?',
                       'Kannst du das anders sagen?',
                       'Mein Entwickler hat zuwenig Möglichkeiten zu antworten programmiert'])
