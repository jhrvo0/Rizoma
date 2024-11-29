// cypress/support/index.js
Cypress.on('uncaught:exception', (err, runnable) => {
    if (err.message.includes('Cannot read properties of null')) {
      return false;
    }
    return true;
  });
  
  describe('Testes Visualizar Campos Preenchidos', () => {
  
    before(() => {
        cy.visit('/')
        cy.get('#email').type('teste@teste.com')
        cy.get('#password').type('yuri1234')
        cy.get('.space-y-4 > .bg-gray-500').click()
        cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
        cy.wait(1000)
        cy.get('#fab-icon').click()
        cy.get('.bg-slate > .font-bold').click()
        cy.get('#id_nome').type('Teste A')
        cy.get('#id_descricao').type('Teste A')
        cy.get('#id_tipo_campo').select('Horta')
        cy.get('#id_tipo_solo').select('Argiloso')
        cy.get('#submit-button').click()
        cy.wait(1000)
        cy.get('#fab-icon').click()
        cy.get('.bg-slate > .font-bold').click()
        cy.get('#id_nome').type('Teste B')
        cy.get('#id_descricao').type('Teste B')
        cy.get('#id_tipo_campo').select('Horta')
        cy.get('#id_tipo_solo').select('Argiloso')
        cy.get('#submit-button').click()
    });
  
    it('Visualizar campos', () => {
      cy.get('.flex.h-16 > .text-center')
      cy.get('.flex-1 > .text-gray-800').then((elements) => {
        const texts = Array.from(elements).map(el => el.innerText.trim());
        expect(texts).to.deep.equal(['Teste A', 'Teste B']);
      });
    });  
  
    it('Visualizar campos e filtrar de A a Z', () => {
      cy.visit('/')
      cy.get('#email').type('teste@teste.com')
      cy.get('#password').type('yuri1234')
      cy.get('.space-y-4 > .bg-gray-500').click()
      cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
  
      cy.get('#filter-button').click()
      cy.get('[data-sort="az"]').click()
      cy.get('.flex-1 > .text-gray-800').then((elements) => {
        const texts = Array.from(elements).map(el => el.innerText.trim());
        expect(texts).to.deep.equal(['Teste A', 'Teste B']);
      });
    });
  
    it('Visualizar campos e filtrar de Z a A', () => {
      cy.visit('/')
      cy.get('#email').type('teste@teste.com')
      cy.get('#password').type('yuri1234')
      cy.get('.space-y-4 > .bg-gray-500').click()
      cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
  
      cy.get('#filter-button').click()
      cy.get('[data-sort="za"]').click()
      cy.get('.flex-1 > .text-gray-800').then((elements) => {
        const texts = Array.from(elements).map(el => el.innerText.trim());
        expect(texts).to.deep.equal(['Teste B', 'Teste A']);
      });
    });
  
    it('Visualizar campos e filtrar por mais recentes', () => {
      cy.visit('/')
      cy.get('#email').type('teste@teste.com')
      cy.get('#password').type('yuri1234')
      cy.get('.space-y-4 > .bg-gray-500').click()
      cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
    
      cy.get('#filter-button').click()
      cy.get('[data-sort="recent"]').click()
    
      cy.get('.flex-1 > .text-gray-800').then((elements) => {
        const texts = Array.from(elements).map(el => el.innerText.trim());
        expect(texts).to.deep.equal(['Teste B', 'Teste A']);
      });
    });
  
    after(() => {
      cy.visit('/')
      cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
  
      cy.get('.flex-1 > .text-gray-800').each((element, index, list) => {
        cy.wrap(element)
          .trigger('mousedown', { which: 1 })
          .wait(1000)
          .trigger('mouseup', { force: true });
  
        if (index === list.length - 1) {
          cy.get('#delete-selected').should('be.visible').click();
          cy.get('#confirm-delete').should('be.visible').click();
        }
      });
    });
  
  });