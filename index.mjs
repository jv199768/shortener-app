let html; // this is reused between invocations
export const handler = async (event) => {
  // TODO implement
  const response = {
    statusCode: 200,
    body: await loadHtml(),
    headers: {
      'content-type': 'text/html; charset=UTF-8'
      }
  };
  return response;
};
const loadHtml = async () => {
  if (!html) {
    // load HTML from somewhere
    // this is only run during cold start and then cached
  }
  return html
}