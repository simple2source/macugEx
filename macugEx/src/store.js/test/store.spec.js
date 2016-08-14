import { expect } from 'chai';
import Store from '../lib/store.js';

describe('Store test', () => {
  it('Store#get string', () => {
    Store.set('string', 'string');
    expect(Store.get('string')).to.be.equal('string');
  });

  it('Store#get int', () => {
    Store.set('int', 1);
    expect(Store.get('int')).to.be.equal(1);
  });

  it('Store#get object', () => {
    Store.set('object', {'key': 'value'});
    expect(Store.get('object')).to.be.an('object');
    expect(Store.get('object')).to.be.deep.equal({'key': 'value'});
  });

  it('Store#get expire', (done) => {
    Store.set('test', 'value', 1000);
    expect(Store.get('test')).to.be.equal('value');
    setTimeout(() => {
      expect(Store.get('test')).to.be.equal(null);
      done();
    }, 1001);
  });

});
