describe('template spec', () => {
    it('Criar campo', () => {
      cy.visit('rizomaapp-g9atb2czhsfyefad.eastus2-01.azurewebsites.net')
      cy.get('#email').type('teste@teste.com')
      cy.get('#password').type('yuri1234')
      cy.get('.space-y-4 > .bg-gray-500').click()
      cy.get('[href="/campos/"]').click()
      cy.get('[href="/campos/43/"] > .bg-gray-300 > .my-auto > .text-gray-800').click()
        cy.get('#fab-icon').click()
    })
  })