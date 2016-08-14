export function createTypes(name) {
  const types = {
    REQUEST: `${name}@REQUEST`,
    SUCCESS: `${name}@SUCCESS`,
    FAILURE: `${name}@FAILURE`
  };
  return types;
}
