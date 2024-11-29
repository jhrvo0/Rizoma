Cypress.on('uncaught:exception', (err, runnable) => {
  if (err.message.includes('Cannot read properties of null')) {
    return false;
  }
  return true;
});

describe('Testes adicionar campos', () => {
  it('Criar campo completo', () => {
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
    cy.get('#popup-container > #popup-modal > .text-2xl')
      .invoke('text')
      .then((text) => {
        expect(text.trim()).to.equal('Campo adicionado com sucesso!')
      });
  })

  it('Criar campo sem colocar nome', () => {
    cy.visit('/')
    cy.get('#email').type('teste@teste.com')
    cy.get('#password').type('yuri1234')
    cy.get('.space-y-4 > .bg-gray-500').click()
    cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
    cy.wait(1000)
    cy.get('#fab-icon').click()
    cy.get('.bg-slate > .font-bold').click()
    cy.get('#id_descricao').type('Teste A')
    cy.get('#id_tipo_campo').select('Horta')
    cy.get('#id_tipo_solo').select('Argiloso')
    cy.get('#submit-button').click()
    // Adicione o interceptador de alertas antes do clique no botão de submit 
    cy.on('window:alert', (alertText) => { 
      expect(alertText).to.contains('Erro ao editar o campo: undefined');
    });
  })

  it('Criar campo sem colocar descrição', () => {
    cy.visit('/')
    cy.get('#email').type('teste@teste.com')
    cy.get('#password').type('yuri1234')
    cy.get('.space-y-4 > .bg-gray-500').click()
    cy.get(':nth-child(2) > .flex > .h-10').should('be.visible').click()
    cy.wait(1000)
    cy.get('#fab-icon').click()
    cy.get('.bg-slate > .font-bold').click()
    cy.get('#id_nome').type('Teste A')
    cy.get('#id_tipo_campo').select('Horta')
    cy.get('#id_tipo_solo').select('Argiloso')
    cy.get('#submit-button').click()
    cy.get('#popup-container > #popup-modal > .text-2xl')
      .invoke('text')
      .then((text) => {
        expect(text.trim()).to.equal('Campo adicionado com sucesso!')
      });
  })

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