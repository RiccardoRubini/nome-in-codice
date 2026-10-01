const endpoint = 'https://classifier.dev/v1/classify';

export async function classifyClue(clue, cards, signal) {
  const related = `collegata all’indizio ${clue}`;
  const unrelated = `non collegata all’indizio ${clue}`;
  let response;
  try {
    response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        inputs: cards.map((card) => card.word),
        labels: [related, unrelated],
        instructions: `Gioco italiano di associazione di parole. Valuta ogni parola rispetto all’indizio «${clue}». Considera legami semantici e usi figurati plausibili. Non conosci l’identità delle carte.`
      }),
      signal,
      cache: 'no-store'
    });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new Error('Servizio AI non raggiungibile. Riprova più tardi.');
  }
  if (!response.ok) {
    if (response.status === 429)
      throw new Error('Limite gratuito del servizio AI raggiunto. Riprova più tardi.');
    if (response.status === 403)
      throw new Error('Il servizio AI non è disponibile da questa rete.');
    throw new Error('Il servizio AI non ha completato la valutazione. Riprova.');
  }
  const data = await response.json().catch(() => null);
  if (
    !Array.isArray(data?.results) ||
    data.results.length !== cards.length ||
    data.results.some((result) => ![related, unrelated].includes(result?.label))
  )
    throw new Error('Il servizio AI ha restituito una risposta incompleta. Riprova.');
  return cards.map((card, position) => {
    const result = data.results[position];
    const score = result?.scores?.[related];
    return {
      ...card,
      related: result?.label === related,
      score: typeof score === 'number' && Number.isFinite(score) ? score : null
    };
  });
}
