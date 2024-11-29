// cypress/support/index.js
Cypress.on('uncaught:exception', (err, runnable) => {
  if (err.message.includes('Cannot read properties of null')) {
    return false;
  }
  return true;
});

describe('Testes Visualizar Campos Vazios', () => {
  it('Visualizar campos vazios', () => {
    cy.visit('/')
    cy.get('#email').type('teste@teste.com')
    cy.get('#password').type('yuri1234')
    cy.get('.space-y-4 > .bg-gray-500').click()
    cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
    cy.get('.p-4 > .text-center')
      .invoke('text')
      .then((text) => {
        expect(text.trim()).to.equal('Clique no "+" e adicione um campo para continuar')
      });
  });
  
  it('Visualizar campos vazios e filtrar de A a Z', () => {
    cy.visit('/')
    cy.get('#email').type('teste@teste.com')
    cy.get('#password').type('yuri1234')
    cy.get('.space-y-4 > .bg-gray-500').click()
    cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
    cy.get('.p-4 > .text-center')
      .invoke('text')
      .then((text) => {
        expect(text.trim()).to.equal('Clique no "+" e adicione um campo para continuar')
      });
    cy.get('#filter-button').click()
    cy.get('[data-sort="az"]').click()
    cy.get('.p-4 > .text-gray-600')
      .invoke('text')
      .then((text) => {
        expect(text.trim()).to.equal('Nenhum campo encontrado.')
      });
  });

  it('Visualizar campos vazios e filtrar de Z a A', () => {
    cy.visit('/')
    cy.get('#email').type('teste@teste.com')
    cy.get('#password').type('yuri1234')
    cy.get('.space-y-4 > .bg-gray-500').click()
    cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
    cy.get('.p-4 > .text-center')
      .invoke('text')
      .then((text) => {
        expect(text.trim()).to.equal('Clique no "+" e adicione um campo para continuar')
      });
    cy.get('#filter-button').click()
    cy.get('[data-sort="za"]').click()
    cy.get('.p-4 > .text-gray-600')
      .invoke('text')
      .then((text) => {
        expect(text.trim()).to.equal('Nenhum campo encontrado.')
      });
    });

  it('Visualizar campos vazios e filtrar por mais recentes', () => {
    cy.visit('/')
    cy.get('#email').type('teste@teste.com')
    cy.get('#password').type('yuri1234')
    cy.get('.space-y-4 > .bg-gray-500').click()
    cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
    cy.get('.p-4 > .text-center')
      .invoke('text')
      .then((text) => {
        expect(text.trim()).to.equal('Clique no "+" e adicione um campo para continuar')
      });
    cy.get('#filter-button').click()
    cy.get('[data-sort="recent"]').click()
    cy.get('.p-4 > .text-gray-600')
      .invoke('text')
      .then((text) => {
        expect(text.trim()).to.equal('Nenhum campo encontrado.')
      });
  });

  it('Visualizar campos vazios e usar ferramenta de pesquisa', () => {
    cy.visit('/')
    cy.get('#email').type('teste@teste.com')
    cy.get('#password').type('yuri1234')
    cy.get('.space-y-4 > .bg-gray-500').click()
    cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
    cy.get('.p-4 > .text-center')
      .invoke('text')
      .then((text) => {
        expect(text.trim()).to.equal('Clique no "+" e adicione um campo para continuar')
      });
    cy.get('#search-input').type('teste')
    cy.get('#search-button').click()
    cy.get('.p-4 > .text-gray-600')
      .invoke('text')
      .then((text) => {
        expect(text.trim()).to.equal('Nenhum campo encontrado.')
      });
    });
});
