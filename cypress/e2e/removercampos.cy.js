Cypress.on('uncaught:exception', (err, runnable) => {
  if (err.message.includes('Cannot read properties of null')) {
    return false;
  }
  return true;
});

describe('Testes Remover Campos', () => {

  beforeEach(() => {
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
  });

  it('Remover um campo existente', () => {
    cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
  
    // Encontre o campo específico "Teste A" e segure para apagá-lo
    cy.get('.field-item > .flex-1').contains('Teste A').parent().as('campoTesteA');
    cy.wait(1000)
  
    cy.get('@campoTesteA')
      .trigger('mousedown', { which: 1 })
      .wait(1000)
      .trigger('mouseup', { force: true });
      cy.wait(1000)
  
    // Clique para deletar e confirmar a remoção
    cy.get('#delete-selected').should('be.visible').click();
    cy.get('#confirm-delete').should('be.visible').click();
    cy.get('#confirm-button').should('be.visible').click();

    cy.get('.p-4 > .text-center')
      .invoke('text')
      .then((text) => {
        expect(text.trim()).to.equal('Clique no "+" e adicione um campo para continuar')
      });
  });  

  it('Remover todos os campos existentes', () => {
      cy.wait(1000)
      cy.get('#fab-icon').click()
      cy.get('.bg-slate > .font-bold').click()
      cy.get('#id_nome').type('Teste B')
      cy.get('#id_descricao').type('Teste B')
      cy.get('#id_tipo_campo').select('Horta')
      cy.get('#id_tipo_solo').select('Argiloso')
      cy.get('#submit-button').click()
      cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
      cy.wait(1000)
  
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