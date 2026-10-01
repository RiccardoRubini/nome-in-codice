"""Pure game rules. No persistence or HTTP dependencies."""
import copy
import random
import re
import secrets

COLORS = ['#a93f36', '#34658a', '#8a681d', '#67508e', '#347268']


class RuleError(ValueError):
    pass


def create_game(config, words):
    teams = config['teams']
    size = config['size']
    if size not in (25, 30) or not 2 <= len(teams) <= 5:
        raise RuleError('Scegli 2–5 squadre e un tabellone da 25 o 30 carte.')
    if len({t['name'].strip().casefold() for t in teams}) != len(teams):
        raise RuleError('Dai un nome diverso a ogni squadra.')
    if len({t['color'] for t in teams}) != len(teams):
        raise RuleError('Scegli un colore diverso per ogni squadra.')
    for t in teams:
        if not 1 <= len(t['name'].strip()) <= 24 or t['color'] not in COLORS or not 1 <= t['cards'] <= size:
            raise RuleError('Controlla nomi, colori e numero di agenti delle squadre.')
    civilians, assassins = config['civilians'], config['assassins']
    if not 0 <= civilians <= size or not 0 <= assassins <= size:
        raise RuleError('Il numero di civili e assassini non è valido.')
    if sum(t['cards'] for t in teams) + civilians + assassins != size:
        raise RuleError('La somma delle carte deve riempire esattamente il tabellone.')
    if len(set(words)) < size:
        raise RuleError('Il dizionario non contiene abbastanza parole.')
    rng = random.SystemRandom()
    assignments = [i for i, t in enumerate(teams) for _ in range(t['cards'])]
    assignments += ['civilian'] * civilians + ['assassin'] * assassins
    rng.shuffle(assignments)
    chosen = rng.sample(list(dict.fromkeys(words)), size)
    return {
        'id': ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(6)),
        'revision': 0, 'size': size, 'status': 'playing', 'winner': None,
        'teams': [dict(name=t['name'].strip(), color=t['color'], total=t['cards'], eliminated=False) for t in teams],
        'cards': [dict(word=w, owner=o, revealed=False) for w, o in zip(chosen, assignments)],
        'active': rng.randrange(len(teams)), 'turn': 1, 'clue': None, 'guesses_left': 0,
        'history': [],
    }


def remaining(game, team):
    return sum(not c['revealed'] and c['owner'] == team for c in game['cards'])


def effective_owner(game, card):
    owner = card['owner']
    if isinstance(owner, int) and game['teams'][owner]['eliminated']:
        return 'civilian'
    return owner


def advance(game):
    for step in range(1, len(game['teams']) + 1):
        candidate = (game['active'] + step) % len(game['teams'])
        if not game['teams'][candidate]['eliminated']:
            game['active'] = candidate
            break
    game['turn'] += 1
    game['clue'] = None
    game['guesses_left'] = 0


def victory(game):
    alive = [i for i,t in enumerate(game['teams']) if not t['eliminated']]
    winners = [i for i in alive if remaining(game,i) == 0]
    if winners or len(alive) == 1:
        game['winner'] = winners[0] if winners else alive[0]
        game['status'] = 'finished'
        game['clue'] = None
        game['guesses_left'] = 0
        return True
    return False


def act(original, command):
    game = copy.deepcopy(original)
    if game['status'] != 'playing':
        raise RuleError('La partita è terminata. Crea una nuova missione.')
    kind = command['kind']
    team = game['active']
    event = {'turn': game['turn'], 'team': team, 'kind': kind}
    if kind == 'clue':
        if game['clue'] is not None:
            raise RuleError('L’indizio di questo turno è già stato dato.')
        word = command.get('word', '').strip()
        number = command.get('number', 1)
        if not re.fullmatch(r"[^\W\d_]+(?:[-’'][^\W\d_]+)?", word) or len(word) > 32:
            raise RuleError('Scrivi un indizio di una sola parola, senza numeri.')
        if any(c['word'].casefold() == word.casefold() for c in game['cards'] if not c['revealed']):
            raise RuleError('L’indizio non può essere una parola ancora coperta sul tabellone.')
        if type(number) is not int or not 0 <= number <= remaining(game, team):
            raise RuleError('Il numero supera gli agenti rimasti; usa 0 per tentativi illimitati.')
        game['clue'] = {'word': word, 'number': number}
        game['guesses_left'] = None if number == 0 else number + 1
        event.update(word=word, number=number)
    elif kind == 'pass':
        advance(game)
    elif kind == 'reveal':
        if game['clue'] is None:
            raise RuleError('Inserisci l’indizio prima di rivelare una carta.')
        index = command.get('card')
        if type(index) is not int or not 0 <= index < len(game['cards']):
            raise RuleError('Carta non valida.')
        card = game['cards'][index]
        if card['revealed']:
            raise RuleError('Questa carta è già stata rivelata.')
        owner = effective_owner(game, card)
        card['revealed'] = True
        card['revealed_as'] = owner
        event.update(word=card['word'], owner=owner, card=index)
        if owner == 'assassin':
            game['teams'][team]['eliminated'] = True
        if not victory(game):
            if owner != team:
                advance(game)
            elif game['guesses_left'] is not None:
                game['guesses_left'] -= 1
                if game['guesses_left'] == 0:
                    advance(game)
    else:
        raise RuleError('Azione non riconosciuta.')
    game['history'] = (game['history'] + [event])[-150:]
    game['revision'] += 1
    return game


def view(game, spy=False):
    result = copy.deepcopy(game)
    for i, team in enumerate(result['teams']):
        team['remaining'] = remaining(game, i)
    for card in result['cards']:
        owner = card.get('revealed_as', effective_owner(game, card))
        card.pop('revealed_as', None)
        if spy or card['revealed'] or game['status'] == 'finished':
            card['owner'] = owner
        else:
            card.pop('owner', None)
    return result
